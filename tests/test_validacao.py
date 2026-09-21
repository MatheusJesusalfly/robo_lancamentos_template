from app.dominio.lancamento import Lancamento
from app.dominio.validacao import conferir


def venda(**troca):
    base = dict(cliente="Ana", descricao="Passagem GRU-LIS",
                faturamento="5360", custo="4800", lucro="560")
    return Lancamento(**(base | troca))


def test_venda_que_fecha_nao_tem_problema():
    assert conferir(venda()) == []


def test_conta_que_nao_fecha_e_apontada_com_os_numeros():
    problemas = conferir(venda(lucro="900"))
    assert len(problemas) == 1
    assert "R$ 5.360,00" in problemas[0]
    assert "R$ 560,00" in problemas[0]
    assert "R$ 900,00" in problemas[0]


def test_diferenca_de_um_centavo_passa():
    """Arredondamento de quem digitou nao pode travar uma venda boa."""
    assert conferir(venda(lucro="560.01")) == []


def test_faturamento_zerado_e_problema():
    assert any("faturamento" in p for p in conferir(venda(faturamento="0", lucro="-4800")))


def test_custo_negativo_e_problema():
    assert any("custo" in p for p in conferir(venda(custo="-10", lucro="5370")))


def test_cliente_vazio_e_problema():
    assert any("cliente" in p for p in conferir(venda(cliente="   ")))


def test_acumula_mais_de_um_problema():
    assert len(conferir(venda(cliente="", faturamento="0", lucro="99"))) >= 2
