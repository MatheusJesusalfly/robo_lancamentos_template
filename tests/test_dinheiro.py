from decimal import Decimal

import pytest

from app.dinheiro import arredondar, em_reais, reais


@pytest.mark.parametrize("entrada,esperado", [
    ("2.043,46", Decimal("2043.46")),
    ("R$ 5360", Decimal("5360.00")),
    ("5.360", Decimal("5360.00")),
    ("1.200,00", Decimal("1200.00")),
    ("0,50", Decimal("0.50")),
    (5360, Decimal("5360.00")),
    (2043.46, Decimal("2043.46")),
    (Decimal("10"), Decimal("10.00")),
    ("560.01", Decimal("560.01")),
    ("1.234.56", Decimal("1234.56")),
])
def test_le_valor_em_varios_formatos(entrada, esperado):
    assert reais(entrada) == esperado


def test_ponto_com_tres_digitos_e_milhar():
    """'5.360' numa agencia brasileira e cinco mil, nao cinco e trinta e seis."""
    assert reais("5.360") == Decimal("5360.00")


def test_ponto_com_dois_digitos_e_decimal():
    """Grupo de milhar tem tres digitos. '560.01' so pode ser decimal -- e e o
    formato que maquina cospe."""
    assert reais("560.01") == Decimal("560.01")


def test_meio_centavo_sobe():
    """O padrao do Python (half-even) mandaria 10,005 para 10,00. Ninguem numa
    agencia espera isso."""
    assert reais("10,005") == Decimal("10.01")


@pytest.mark.parametrize("lixo", ["", "abc", "R$", "  "])
def test_valor_ilegivel_levanta(lixo):
    with pytest.raises(ValueError):
        reais(lixo)


def test_arredonda_para_centavos():
    assert arredondar(Decimal("10.005")) == Decimal("10.01")


@pytest.mark.parametrize("valor,texto", [
    (Decimal("1234.5"), "R$ 1.234,50"),
    (Decimal("999"), "R$ 999,00"),
    (Decimal("1000000"), "R$ 1.000.000,00"),
    (Decimal("-50.25"), "-R$ 50,25"),
])
def test_formata_em_reais(valor, texto):
    assert em_reais(valor) == texto
