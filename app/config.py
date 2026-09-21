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
    #: O "lite" de proposito: medido numa chave nova do plano gratuito, ele
    #: respondeu em ~1,2s enquanto o 3.5-flash e o 3.6-flash devolviam 503. Num
    #: robo que le venda, estar disponivel vale mais que ser o maior modelo.
    #: Nomes de modelo mudam: confira em aistudio.google.com de tempos em
    #: tempos. Se der 404, e isso. A receita esta em docs/RECEITAS.md.
    gemini_modelo: str = "gemini-3.5-flash-lite"
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
