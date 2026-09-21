import json

import httpx
import pytest
import respx

from app.destino.planilha import Planilha
from app.dominio.lancamento import Lancamento

URL = "https://script.google.com/macros/s/abc/exec"
VENDA = Lancamento(cliente="Ana", descricao="Passagem GRU-LIS",
                   faturamento="5360", custo="4800", lucro="560")


@respx.mock
def test_grava_e_devolve_a_linha():
    rota = respx.post(URL).mock(
        return_value=httpx.Response(200, json={"ok": True, "linha": 7}))
    resultado = Planilha(URL, "segredo").escrever(VENDA)
    assert resultado.referencia == "linha 7"
    assert resultado.pendencias == []
    corpo = json.loads(rota.calls.last.request.content)
    assert corpo["segredo"] == "segredo"
    assert corpo["cliente"] == "Ana"
    assert corpo["faturamento"] == "5360.00"


@respx.mock
def test_erro_com_http_200_e_tratado_como_erro():
    """O Apps Script responde 200 mesmo quando recusa, com o erro no corpo. E o
    mesmo defeito da API do Iddas, que ja custou horas: le-se o corpo, nunca o
    status."""
    respx.post(URL).mock(
        return_value=httpx.Response(200, json={"ok": False, "erro": "segredo errado"}))
    with pytest.raises(RuntimeError, match="segredo errado"):
        Planilha(URL, "errado").escrever(VENDA)


@respx.mock
def test_resposta_que_nao_e_json_vira_erro_legivel():
    respx.post(URL).mock(return_value=httpx.Response(200, text="<html>login</html>"))
    with pytest.raises(RuntimeError, match="nao e JSON"):
        Planilha(URL, "segredo").escrever(VENDA)


def test_segue_redirecionamento():
    """O Apps Script responde 302 para script.googleusercontent.com. Sem
    follow_redirects o httpx devolve o 302 e parece que falhou."""
    assert Planilha(URL, "segredo")._http.follow_redirects is True
