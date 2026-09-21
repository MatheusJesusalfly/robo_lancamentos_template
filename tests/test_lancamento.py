from decimal import Decimal

from app.dominio.lancamento import Lancamento


def test_aceita_dinheiro_como_texto_e_como_numero():
    lanc = Lancamento(cliente="Ana", descricao="Passagem GRU-LIS",
                      faturamento="5.360,00", custo=4800, lucro=Decimal("560"))
    assert lanc.faturamento == Decimal("5360.00")
    assert lanc.custo == Decimal("4800.00")
    assert lanc.lucro == Decimal("560.00")


def test_observacao_e_opcional():
    lanc = Lancamento(cliente="Ana", descricao="x", faturamento=1, custo=0, lucro=1)
    assert lanc.observacao == ""
