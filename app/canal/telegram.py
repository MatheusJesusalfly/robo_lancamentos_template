"""A entrada: Telegram, buscando as mensagens sozinho.

Telegram e nao WhatsApp por um motivo pratico, nao ideologico: aqui o robo
PERGUNTA se chegou mensagem (long polling). Nao precisa de endereco publico, nem
de tunel, nem de webhook -- roda no seu computador, atras de qualquer wi-fi. Com
WhatsApp seria preciso um servidor com endereco proprio.

Nem todo update tem quem falou: post de canal, encaminhamento automatico e
admin anonimo chegam sem "from". Quebrar ali seria pior do que parece -- o
offset ja avancou, entao as vendas lidas no mesmo lote sumiriam para sempre.

O offset e a peca que mais quebra robo de Telegram: sem avanca-lo, o robo rele a
mesma mensagem para sempre e responde em loop. Ele avanca inclusive no que foi
ignorado -- senao uma figurinha trava tudo.
"""

from __future__ import annotations

import logging

import httpx

from app.canal.porta import Mensagem

log = logging.getLogger("robo")

#: O Telegram recusa mensagem maior que isto, e o robo so descobriria depois
#: de ja ter gravado a venda.
LIMITE_TELEGRAM = 4000


class Telegram:
    nome = "telegram"

    def __init__(self, token: str, cliente: httpx.Client | None = None,
                 espera: int = 25):
        self._base = f"https://api.telegram.org/bot{token}"
        self._espera = espera
        self._http = cliente or httpx.Client(timeout=espera + 10)
        self._proximo: int | None = None

    def receber(self) -> list[Mensagem]:
        parametros: dict[str, int] = {"timeout": self._espera}
        if self._proximo is not None:
            parametros["offset"] = self._proximo

        resposta = self._http.get(f"{self._base}/getUpdates", params=parametros)
        resposta.raise_for_status()

        mensagens: list[Mensagem] = []
        for item in resposta.json().get("result", []):
            self._proximo = item["update_id"] + 1
            msg = item.get("message") or {}
            texto = msg.get("text")
            quem = (msg.get("from") or {}).get("id")
            onde = (msg.get("chat") or {}).get("id")
            if not texto or quem is None or onde is None:
                continue
            mensagens.append(Mensagem(de=quem, conversa=onde, texto=texto))
        return mensagens

    def responder(self, conversa: int, texto: str) -> None:
        if len(texto) > LIMITE_TELEGRAM:
            texto = texto[:LIMITE_TELEGRAM] + "\n\n[resposta cortada]"

        resposta = self._http.post(f"{self._base}/sendMessage",
                                   json={"chat_id": conversa, "text": texto})

        # Calar aqui e caro: se a confirmacao nao chega depois de gravar, a
        # pessoa acha que falhou, reenvia a venda, e a linha duplica.
        if resposta.status_code != 200:
            log.warning("nao consegui responder em %s: %s %s", conversa,
                        resposta.status_code, resposta.text[:200])
