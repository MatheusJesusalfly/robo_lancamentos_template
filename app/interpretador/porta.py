"""O contrato que todo interpretador cumpre.

Hoje e o Gemini no free tier, porque da para comecar sem cartao de credito.
Quando o dado for de cliente de verdade, trocar por Gemini pago ou por outro
modelo e escrever uma classe com este unico metodo.

A regra de negocio nao muda. E esse o ponto.
"""

from __future__ import annotations

from typing import Protocol

from app.dominio.lancamento import Lancamento


class Interpretador(Protocol):
    nome: str

    def interpretar(self, texto: str) -> Lancamento: ...
