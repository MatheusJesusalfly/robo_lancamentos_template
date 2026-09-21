"""O contrato que toda entrada cumpre.

Duas funcoes: trazer o que chegou, e responder. Trocar o Telegram pelo WhatsApp
e escrever uma classe com estes dois metodos -- e ai sim vem servidor, endereco
publico e webhook, que e o degrau de cima.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class Mensagem:
    #: quem falou, no id do canal. E por ele que o robo sabe se pode obedecer.
    de: int
    #: onde responder.
    conversa: int
    texto: str


class Canal(Protocol):
    nome: str

    def receber(self) -> list[Mensagem]: ...

    def responder(self, conversa: int, texto: str) -> None: ...
