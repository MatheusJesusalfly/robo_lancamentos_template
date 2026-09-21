"""Transforma a mensagem da venda num Lancamento.

ATENCAO AO FREE TIER. No servico nao pago do Gemini, os termos do Google dizem
que o que voce manda e o que volta podem ser usados para melhorar os produtos
deles, e que revisores humanos podem ler o material -- e o proprio Google pede
que nao se mande informacao sensivel, confidencial ou pessoal por ali.

Mensagem de venda tem nome de cliente. Para aprender, tudo bem. Para a sua
operacao de verdade, troque para o tier pago ou para outro modelo: e uma classe,
por causa da porta ao lado.

O MANUAL DA SUA AGENCIA ENTRA NO PROMPT. O texto de manual/MANUAL.md e o que faz
este robo ser o SEU robo. Mudar o comportamento dele e editar aquele arquivo,
nao este.
"""

from __future__ import annotations

import time

import httpx

from app.dominio.lancamento import Lancamento

BASE = "https://generativelanguage.googleapis.com/v1beta"

#: Quanto esperar antes de tentar de novo. Duas esperas, logo tres tentativas.
ESPERAS = (2, 4)

#: Recusa que repetir NAO conserta: chave errada, modelo que nao existe, pedido
#: malformado, quota estourada. Essas sobem na hora -- repetir so faria quem
#: vendeu esperar mais para ler o mesmo erro.
NAO_ADIANTA_REPETIR = {400, 401, 403, 404, 429}

ESQUEMA = {
    "type": "object",
    "properties": {
        "cliente": {"type": "string"},
        "descricao": {"type": "string"},
        "faturamento": {"type": "number"},
        "custo": {"type": "number"},
        "lucro": {"type": "number"},
        "observacao": {"type": "string"},
    },
    "required": ["cliente", "descricao", "faturamento", "custo", "lucro"],
}

INSTRUCAO = """Voce le a mensagem em que alguem de uma agencia de viagens conta uma venda que fechou, e devolve os dados dela.

Regras:
- Valores em reais, como numero: 2043.46. Sem "R$" e sem ponto de milhar.
- lucro = faturamento - custo. Se a mensagem trouxer os tres e a conta nao fechar, devolva o que esta escrito: conferir e trabalho de gente, nao seu.
- Se o lucro nao estiver na mensagem, calcule.
- Nao invente. O que nao estiver na mensagem volta vazio ou zero.

O MANUAL DA AGENCIA manda mais do que estas regras:
---
{manual}
---

A mensagem:
{mensagem}"""


class Gemini:
    nome = "gemini"

    def __init__(self, chave: str, modelo: str, manual: str,
                 cliente: httpx.Client | None = None):
        self._chave = chave
        self._modelo = modelo
        self._manual = manual
        # 30s e nao 60: com tres tentativas, 60 viraria tres minutos de silencio
        # para quem esta esperando o resumo no Telegram. Uma chamada que da
        # certo leva uns 7 segundos.
        self._http = cliente or httpx.Client(timeout=30)

    def interpretar(self, texto: str) -> Lancamento:
        corpo = {
            "contents": [{"parts": [{
                "text": INSTRUCAO.format(manual=self._manual, mensagem=texto)}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": ESQUEMA,
            },
        }
        resposta = self._pedir(corpo)

        try:
            bruto = resposta.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, ValueError):
            raise RuntimeError(
                f"resposta do Gemini fora do formato: {resposta.text[:200]}") from None

        return Lancamento.model_validate_json(bruto)

    def _pedir(self, corpo: dict) -> httpx.Response:
        """Tenta de novo quando o Gemini engasga.

        No plano gratuito o 503 ("alta demanda") e o timeout aparecem sozinhos e
        somem sozinhos, em segundos. Sem esta repeticao o robo leva o primeiro
        nao e devolve erro para quem vendeu -- que digita a venda de novo, as
        vezes na frente do cliente, as vezes na frente de uma turma.
        """
        erro: RuntimeError | None = None

        for tentativa in range(len(ESPERAS) + 1):
            if tentativa:
                time.sleep(ESPERAS[tentativa - 1])

            try:
                resposta = self._http.post(
                    f"{BASE}/models/{self._modelo}:generateContent",
                    headers={"x-goog-api-key": self._chave},
                    json=corpo)
            except httpx.RequestError as falha:
                # Timeout e queda de rede: exatamente o caso que volta sozinho.
                erro = RuntimeError(f"o Gemini nao respondeu: {falha}")
                continue

            if resposta.status_code == 200:
                return resposta

            erro = RuntimeError(
                f"o Gemini recusou ({resposta.status_code}): {resposta.text[:200]}")
            if resposta.status_code in NAO_ADIANTA_REPETIR:
                raise erro

        raise RuntimeError(f"{erro} -- tentei {len(ESPERAS) + 1} vezes")
