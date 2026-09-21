"""Dinheiro e Decimal, sempre.

Numa agencia a margem fica em 5-6%: erro de ponto flutuante nao e detalhe, e a
diferenca entre lucro e prejuizo publicado. float nao entra aqui.
"""

from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

CENTAVOS = Decimal("0.01")
_SO_NUMERO = re.compile(r"[^\d,.\-]")


def arredondar(valor: Decimal) -> Decimal:
    """Meio centavo sobe.

    O padrao do Python e o arredondamento bancario (half-even), que manda
    10,005 para 10,00 porque o zero e par. Ninguem numa agencia espera isso, e
    a surpresa aparece justamente na casa que decide lucro.
    """
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def reais(valor: str | int | float | Decimal) -> Decimal:
    """Le um valor escrito como gente escreve: '2.043,46', 'R$ 5360', '5.360'."""
    if isinstance(valor, bool):
        raise ValueError(f"valor ilegivel: {valor!r}")
    if isinstance(valor, Decimal):
        return arredondar(valor)
    if isinstance(valor, (int, float)):
        return arredondar(Decimal(str(valor)))

    texto = _SO_NUMERO.sub("", str(valor)).strip()
    if not texto or texto in {"-", ",", "."}:
        raise ValueError(f"valor ilegivel: {valor!r}")

    # Em pt-BR a virgula e o decimal e o ponto separa milhar. Sem virgula, o
    # ponto continua sendo milhar: '5.360' e cinco mil, nao cinco e trinta e seis.
    if "," in texto and "." in texto:
        # Quem separa o decimal e o que vier POR ULTIMO. '1.234,56' e
        # brasileiro; '12,500.00' e americano. Confundir os dois nao da erro:
        # da uma venda mil vezes menor, gravada em silencio.
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto:
        texto = texto.replace(",", ".")
    elif re.search(r"\.\d{1,2}$", texto):
        # '560.01' nao pode ser milhar: grupo de milhar tem tres digitos. E o
        # formato que maquina cospe -- e que um humano apressado tambem digita.
        inteiro, _, decimais = texto.rpartition(".")
        texto = f"{inteiro.replace('.', '')}.{decimais}"
    else:
        texto = texto.replace(".", "")

    try:
        return arredondar(Decimal(texto))
    except InvalidOperation:
        raise ValueError(f"valor ilegivel: {valor!r}") from None


def em_reais(valor: Decimal) -> str:
    """Decimal('1234.5') -> 'R$ 1.234,50'."""
    inteiro, _, decimais = f"{arredondar(valor):.2f}".partition(".")
    sinal = "-" if inteiro.startswith("-") else ""
    inteiro = inteiro.lstrip("-")
    grupos = []
    while len(inteiro) > 3:
        grupos.insert(0, inteiro[-3:])
        inteiro = inteiro[:-3]
    grupos.insert(0, inteiro)
    return f"{sinal}R$ {'.'.join(grupos)},{decimais}"
