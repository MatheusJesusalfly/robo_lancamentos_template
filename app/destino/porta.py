"""O contrato que todo destino cumpre.

A regra de negocio nao conhece planilha, Bitrix nem CRM nenhum: conhece esta
porta. Trocar de destino e escrever uma classe com estes dois metodos -- nao e
mexer em regra de negocio.

Repare que Planilha NAO herda de Destino. Protocol e estrutural: basta ter os
metodos certos. E por isso que a sua classe nova nao precisa importar nada daqui.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Protocol

from app.dominio.lancamento import Lancamento

log = logging.getLogger("robo")


@dataclass
class ResultadoEscrita:
    destino: str
    #: como achar depois o que foi escrito: numero da linha, id da venda...
    referencia: str | None = None
    pendencias: list[str] = field(default_factory=list)


class Destino(Protocol):
    nome: str

    def escrever(self, lanc: Lancamento) -> ResultadoEscrita: ...


def escrever_em(destinos: list[Destino], lanc: Lancamento) -> list[ResultadoEscrita]:
    """Escreve em todos, em ordem, e NUNCA aborta no meio.

    Abortar deixaria a venda sem registro nenhum porque um sistema secundario
    piscou. Cada falha vira duas coisas: pendencia no resultado, para quem le a
    resposta do robo, e linha de log, para quem for investigar depois.
    """
    saida: list[ResultadoEscrita] = []
    for destino in destinos:
        try:
            saida.append(destino.escrever(lanc))
        except Exception as erro:
            log.warning("destino %s falhou: %s", destino.nome, erro)
            saida.append(ResultadoEscrita(
                destino=destino.nome, pendencias=[f"{destino.nome}: {erro}"]))
    return saida
