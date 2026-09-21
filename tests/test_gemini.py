import json

import httpx
import pytest
import respx

from app.interpretador.gemini import Gemini

MODELO = "gemini-3.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent"


def resposta_do_modelo(**campos):
    base = {"cliente": "Ana", "descricao": "Passagem GRU-LIS",
            "faturamento": 5360, "custo": 4800, "lucro": 560, "observacao": ""}
    return httpx.Response(200, json={"candidates": [
        {"content": {"parts": [{"text": json.dumps(base | campos)}]}}]})


@respx.mock
def test_transforma_a_mensagem_num_lancamento():
    respx.post(URL).mock(return_value=resposta_do_modelo())
    lanc = Gemini("chave", MODELO, "manual").interpretar("vendi pra Ana...")
    assert lanc.cliente == "Ana"
    assert str(lanc.faturamento) == "5360.00"
    assert str(lanc.lucro) == "560.00"


@respx.mock
def test_decimal_do_modelo_nao_vira_milhar():
    """O modelo devolve 560.01 no formato de maquina. Se isso passasse pela
    regra do ponto-e-milhar, viraria R$ 56.001,00."""
    respx.post(URL).mock(return_value=resposta_do_modelo(lucro=560.01, custo=4799.99))
    lanc = Gemini("chave", MODELO, "").interpretar("x")
    assert str(lanc.lucro) == "560.01"
    assert str(lanc.custo) == "4799.99"


@respx.mock
def test_manda_o_manual_e_a_mensagem_no_prompt():
    """O manual que o dono da agencia escreveu E o comportamento do robo."""
    rota = respx.post(URL).mock(return_value=resposta_do_modelo())
    Gemini("chave", MODELO, "REGRA: comissao entra sozinha").interpretar("vendi X")
    prompt = json.loads(rota.calls.last.request.content)["contents"][0]["parts"][0]["text"]
    assert "REGRA: comissao entra sozinha" in prompt
    assert "vendi X" in prompt


@respx.mock
def test_pede_json_estruturado():
    rota = respx.post(URL).mock(return_value=resposta_do_modelo())
    Gemini("chave", MODELO, "").interpretar("vendi X")
    config = json.loads(rota.calls.last.request.content)["generationConfig"]
    assert config["responseMimeType"] == "application/json"
    assert set(config["responseSchema"]["required"]) == {
        "cliente", "descricao", "faturamento", "custo", "lucro"}


@respx.mock
def test_manda_a_chave_no_header():
    rota = respx.post(URL).mock(return_value=resposta_do_modelo())
    Gemini("chave-secreta", MODELO, "").interpretar("vendi X")
    assert rota.calls.last.request.headers["x-goog-api-key"] == "chave-secreta"


@respx.mock
def test_erro_do_gemini_vira_mensagem_legivel():
    respx.post(URL).mock(return_value=httpx.Response(429, text="quota esgotada"))
    with pytest.raises(RuntimeError, match="429"):
        Gemini("chave", MODELO, "").interpretar("vendi X")


@respx.mock
def test_resposta_fora_do_formato_vira_mensagem_legivel():
    respx.post(URL).mock(return_value=httpx.Response(200, json={"promptFeedback": {}}))
    with pytest.raises(RuntimeError, match="fora do formato"):
        Gemini("chave", MODELO, "").interpretar("vendi X")


@pytest.fixture
def sem_espera(monkeypatch):
    """A regra e repetir, nao esperar. O teste nao precisa dos 6 segundos."""
    monkeypatch.setattr("app.interpretador.gemini.ESPERAS", (0, 0))


@respx.mock
def test_repete_quando_o_gemini_diz_que_esta_com_alta_demanda(sem_espera):
    """503 no plano gratuito vai e volta em segundos. Desistir na primeira faz
    quem vendeu digitar a venda de novo."""
    rota = respx.post(URL).mock(side_effect=[
        httpx.Response(503, text="high demand"),
        httpx.Response(503, text="high demand"),
        resposta_do_modelo()])
    lanc = Gemini("chave", MODELO, "").interpretar("vendi X")
    assert lanc.cliente == "Ana"
    assert rota.call_count == 3


@respx.mock
def test_repete_quando_o_gemini_nao_responde_a_tempo(sem_espera):
    rota = respx.post(URL).mock(side_effect=[
        httpx.ReadTimeout("The read operation timed out"),
        resposta_do_modelo()])
    assert Gemini("chave", MODELO, "").interpretar("vendi X").cliente == "Ana"
    assert rota.call_count == 2


@respx.mock
def test_desiste_depois_de_tres_tentativas(sem_espera):
    rota = respx.post(URL).mock(return_value=httpx.Response(503, text="high demand"))
    with pytest.raises(RuntimeError, match="tentei 3 vezes"):
        Gemini("chave", MODELO, "").interpretar("vendi X")
    assert rota.call_count == 3


@respx.mock
def test_nao_repete_o_que_repetir_nao_conserta(sem_espera):
    """Chave errada continua errada na terceira tentativa. Subir na hora e o
    favor que se faz a quem esta esperando."""
    rota = respx.post(URL).mock(return_value=httpx.Response(401, text="API key invalid"))
    with pytest.raises(RuntimeError, match="401"):
        Gemini("chave-errada", MODELO, "").interpretar("vendi X")
    assert rota.call_count == 1
