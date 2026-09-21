from app.destino.porta import ResultadoEscrita, escrever_em
from app.dominio.lancamento import Lancamento

VENDA = Lancamento(cliente="Ana", descricao="x", faturamento=100, custo=40, lucro=60)


class DestinoFalso:
    def __init__(self, nome, erro=None):
        self.nome = nome
        self._erro = erro
        self.escreveu = []

    def escrever(self, lanc):
        if self._erro:
            raise RuntimeError(self._erro)
        self.escreveu.append(lanc)
        return ResultadoEscrita(destino=self.nome, referencia="linha 2")


def test_escreve_em_todos_na_ordem():
    a, b = DestinoFalso("a"), DestinoFalso("b")
    saida = escrever_em([a, b], VENDA)
    assert [r.destino for r in saida] == ["a", "b"]
    assert a.escreveu and b.escreveu


def test_falha_de_um_destino_nao_aborta_os_outros():
    """Abortar deixaria a venda sem registro nenhum porque um sistema
    secundario piscou."""
    quebrado, bom = DestinoFalso("quebrado", erro="caiu"), DestinoFalso("bom")
    saida = escrever_em([quebrado, bom], VENDA)
    assert saida[0].pendencias == ["quebrado: caiu"]
    assert saida[1].referencia == "linha 2"
    assert bom.escreveu
