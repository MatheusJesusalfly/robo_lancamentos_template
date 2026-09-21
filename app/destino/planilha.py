"""Grava a linha numa planilha do Google, por Apps Script.

Apps Script e nao conta de servico do Google Cloud: conta de servico e um muro
para quem nao e tecnico, e ha organizacoes que nem permitem criar a chave.

Duas armadilhas, as duas ja custaram horas em projeto de verdade:

1. O Apps Script responde 302 para script.googleusercontent.com. Sem
   follow_redirects o httpx devolve o 302 e parece que a escrita falhou.
2. Ele responde HTTP 200 mesmo quando recusa, com o erro no corpo. E o mesmo
   defeito da API do Iddas. Por isso aqui se le o CORPO, nunca o status.
"""

from __future__ import annotations

import httpx

from app.destino.porta import ResultadoEscrita
from app.dominio.lancamento import Lancamento


class Planilha:
    nome = "planilha"

    def __init__(self, url: str, segredo: str, cliente: httpx.Client | None = None):
        self._url = url
        self._segredo = segredo
        self._http = cliente or httpx.Client(timeout=30, follow_redirects=True)

    def escrever(self, lanc: Lancamento) -> ResultadoEscrita:
        corpo = {
            "segredo": self._segredo,
            "cliente": lanc.cliente,
            "descricao": lanc.descricao,
            "faturamento": str(lanc.faturamento),
            "custo": str(lanc.custo),
            "lucro": str(lanc.lucro),
            "observacao": lanc.observacao,
        }
        resposta = self._http.post(self._url, json=corpo)

        try:
            dados = resposta.json()
        except ValueError:
            raise RuntimeError(
                f"a planilha respondeu algo que nao e JSON: {resposta.text[:200]}"
            ) from None

        if not dados.get("ok"):
            raise RuntimeError(f"a planilha recusou: {dados.get('erro', dados)}")

        # .get e nao ['linha']: um Apps Script antigo ainda implantado responde
        # sem o numero, e o KeyError viraria "planilha: 'linha'" para alguem que
        # nao tem como entender isso -- sugerindo falha numa linha que gravou.
        return ResultadoEscrita(destino=self.nome,
                                referencia=f"linha {dados.get('linha', '?')}")
