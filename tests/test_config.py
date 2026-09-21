from app.config import Config


def test_lista_vazia_nao_autoriza_ninguem():
    """Vazio significa NINGUEM. Um robo que escreve e nao sabe a quem obedecer
    e pior ligado do que desligado."""
    assert Config(autorizados="").pode_lancar(123) is False


def test_autoriza_quem_esta_na_lista():
    config = Config(autorizados="123,456")
    assert config.pode_lancar(123) is True
    assert config.pode_lancar(456) is True
    assert config.pode_lancar(789) is False


def test_ignora_espacos_na_lista():
    assert Config(autorizados=" 123 , 456 ").pode_lancar(456) is True


def test_modelo_tem_padrao():
    """O "-lite" e escolha, nao acaso: numa chave nova do plano gratuito ele
    respondeu enquanto os outros davam 503. Se este teste quebrar porque alguem
    trocou o padrao, confira antes se o modelo novo aguenta a fila."""
    assert Config().gemini_modelo == "gemini-3.5-flash-lite"
