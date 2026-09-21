import json

import httpx
import respx

from app.canal.telegram import Telegram

TOKEN = "123:ABC"
BASE = f"https://api.telegram.org/bot{TOKEN}"


def atualizacao(update_id, texto, de=42, chat=42):
    return {"update_id": update_id,
            "message": {"from": {"id": de}, "chat": {"id": chat}, "text": texto}}


@respx.mock
def test_le_as_mensagens():
    respx.get(f"{BASE}/getUpdates").mock(return_value=httpx.Response(
        200, json={"ok": True, "result": [atualizacao(1, "vendi pra Ana")]}))
    mensagens = Telegram(TOKEN).receber()
    assert len(mensagens) == 1
    assert mensagens[0].texto == "vendi pra Ana"
    assert mensagens[0].de == 42
    assert mensagens[0].conversa == 42


@respx.mock
def test_nao_le_a_mesma_mensagem_duas_vezes():
    """Sem avancar o offset o robo responde a mesma venda para sempre."""
    rota = respx.get(f"{BASE}/getUpdates").mock(side_effect=[
        httpx.Response(200, json={"ok": True, "result": [atualizacao(7, "oi")]}),
        httpx.Response(200, json={"ok": True, "result": []}),
    ])
    canal = Telegram(TOKEN)
    canal.receber()
    canal.receber()
    assert rota.calls[1].request.url.params["offset"] == "8"


@respx.mock
def test_ignora_o_que_nao_tem_texto():
    """Figurinha, foto e entrada em grupo chegam sem 'text' e quebrariam tudo."""
    respx.get(f"{BASE}/getUpdates").mock(return_value=httpx.Response(200, json={
        "ok": True, "result": [
            {"update_id": 1, "message": {"from": {"id": 1}, "chat": {"id": 1}}},
            {"update_id": 2, "edited_message": {"text": "x"}},
            atualizacao(3, "vendi"),
        ]}))
    assert [m.texto for m in Telegram(TOKEN).receber()] == ["vendi"]


@respx.mock
def test_avanca_o_offset_mesmo_no_que_ignorou():
    """Senao uma figurinha trava o robo: ele rele a mesma atualizacao sempre."""
    rota = respx.get(f"{BASE}/getUpdates").mock(side_effect=[
        httpx.Response(200, json={"ok": True, "result": [
            {"update_id": 9, "message": {"from": {"id": 1}, "chat": {"id": 1}}}]}),
        httpx.Response(200, json={"ok": True, "result": []}),
    ])
    canal = Telegram(TOKEN)
    canal.receber()
    canal.receber()
    assert rota.calls[1].request.url.params["offset"] == "10"


@respx.mock
def test_responde_na_conversa_certa():
    rota = respx.post(f"{BASE}/sendMessage").mock(
        return_value=httpx.Response(200, json={"ok": True}))
    Telegram(TOKEN).responder(99, "gravei")
    assert json.loads(rota.calls.last.request.content) == {"chat_id": 99, "text": "gravei"}


@respx.mock
def test_update_sem_quem_falou_nao_derruba_o_lote():
    """Post de canal e admin anonimo chegam sem 'from'. Quebrar aqui perderia
    as vendas lidas no mesmo lote -- e o offset ja avancou, entao elas nunca
    voltariam."""
    respx.get(f"{BASE}/getUpdates").mock(return_value=httpx.Response(200, json={
        "ok": True, "result": [
            {"update_id": 1, "message": {"chat": {"id": 9}, "text": "post do canal"}},
            atualizacao(2, "vendi 5360"),
        ]}))
    assert [m.texto for m in Telegram(TOKEN).receber()] == ["vendi 5360"]


@respx.mock
def test_resposta_gigante_e_cortada():
    """O Telegram recusa acima de 4096 caracteres, e o robo so descobriria
    depois de ja ter gravado a venda."""
    rota = respx.post(f"{BASE}/sendMessage").mock(
        return_value=httpx.Response(200, json={"ok": True}))
    Telegram(TOKEN).responder(1, "x" * 9000)
    enviado = json.loads(rota.calls.last.request.content)["text"]
    assert len(enviado) < 4100
    assert enviado.endswith("[resposta cortada]")


@respx.mock
def test_recusa_do_telegram_vira_log_e_nao_excecao(caplog):
    """Se estourar aqui depois de gravar, a pessoa reenvia a venda e duplica
    a linha."""
    respx.post(f"{BASE}/sendMessage").mock(
        return_value=httpx.Response(403, text="bot was blocked by the user"))
    Telegram(TOKEN).responder(1, "gravei")
    assert "nao consegui responder" in caplog.text
