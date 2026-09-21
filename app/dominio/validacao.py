"""A conta fecha?

Um robo que chuta quando nao fecha e pior que robo nenhum: ele grava um numero
errado com cara de conferido. Aqui ele so sabe dizer o que ficou estranho --
quem decide continua sendo gente.
"""

from __future__ import annotations

from app.dinheiro import CENTAVOS, em_reais
from app.dominio.lancamento import Lancamento


def conferir(lanc: Lancamento) -> list[str]:
    """Problemas em portugues de gente. Lista vazia significa pode gravar."""
    problemas: list[str] = []

    if not lanc.cliente.strip():
        problemas.append("nao achei o nome do cliente")
    if lanc.faturamento <= 0:
        problemas.append("o faturamento veio zerado")
    if lanc.custo < 0:
        problemas.append("o custo veio negativo")

    esperado = lanc.faturamento - lanc.custo
    if abs(esperado - lanc.lucro) > CENTAVOS:
        problemas.append(
            f"a conta nao fecha: {em_reais(lanc.faturamento)} menos "
            f"{em_reais(lanc.custo)} da {em_reais(esperado)}, "
            f"e nao {em_reais(lanc.lucro)}")

    return problemas
