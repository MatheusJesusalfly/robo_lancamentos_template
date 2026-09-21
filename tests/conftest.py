"""Isola os testes do .env da maquina.

Sem isto, `Config()` dentro de um teste le o .env real de quem roda: o resultado
muda conforme a maquina, e chave de verdade vaza para dentro do teste.
"""

import pytest

from app.config import Config


@pytest.fixture(autouse=True)
def _config_sem_env_da_maquina(monkeypatch):
    monkeypatch.setitem(Config.model_config, "env_file", None)
    for chave in ("TELEGRAM_TOKEN", "GEMINI_API_KEY", "GEMINI_MODELO",
                  "PLANILHA_URL", "PLANILHA_SEGREDO", "AUTORIZADOS"):
        monkeypatch.delenv(chave, raising=False)
