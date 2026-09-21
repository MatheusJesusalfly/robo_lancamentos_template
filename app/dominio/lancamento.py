"""O que este robo entende por "uma venda".

Os campos sao o minimo que serve a qualquer agencia. O que e especifico da sua
operacao entra no MANUAL, nao aqui -- e so vira campo quando doer de verdade.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, field_validator

from app.dinheiro import reais


class Lancamento(BaseModel):
    cliente: str
    descricao: str
    faturamento: Decimal
    custo: Decimal
    lucro: Decimal
    observacao: str = ""

    @field_validator("faturamento", "custo", "lucro", mode="before")
    @classmethod
    def _como_dinheiro(cls, valor):
        return reais(valor)
