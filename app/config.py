"""Tudo que o robo precisa saber, e nada disso dentro do codigo.

Chave e token moram no .env, que esta no .gitignore: quem publicar este robo no
GitHub nao publica junto a chave do Gemini.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    telegram_token: str = ""
    gemini_api_key: str = ""
    #: Confira o nome do modelo atual no Google AI Studio antes da aula.
    gemini_modelo: str = "gemini-3.5-flash"
    planilha_url: str = ""
    planilha_segredo: str = ""
    #: Ids do Telegram separados por virgula. Descubra o seu com @userinfobot.
    autorizados: str = ""

    def pode_lancar(self, id_telegram: int) -> bool:
        """Lista vazia significa NINGUEM, nao "todo mundo".

        E a mesma escolha do robo da Alfly: aberto por engano, qualquer pessoa
        que ache o bot grava linha na sua planilha.
        """
        permitidos = {p.strip() for p in self.autorizados.split(",") if p.strip()}
        return str(id_telegram) in permitidos
