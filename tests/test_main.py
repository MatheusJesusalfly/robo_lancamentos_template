from app.__main__ import faltando
from app.config import Config


def test_diz_tudo_que_falta_de_uma_vez():
    """Um erro por vez faria a pessoa rodar cinco vezes para descobrir cinco
    coisas. Na vespera da aula isso e meia hora."""
    problemas = faltando(Config())
    assert len(problemas) == 5
    for nome in ("TELEGRAM_TOKEN", "GEMINI_API_KEY", "PLANILHA_URL",
                 "PLANILHA_SEGREDO", "AUTORIZADOS"):
        assert any(nome in p for p in problemas)


def test_config_completa_nao_tem_pendencia():
    completa = Config(telegram_token="t", gemini_api_key="g", planilha_url="u",
                      planilha_segredo="s", autorizados="42")
    assert faltando(completa) == []
