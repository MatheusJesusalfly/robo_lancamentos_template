from app.canal.porta import Mensagem
from app.config import Config
from app.conversa import Conversa
from app.destino.porta import ResultadoEscrita
from app.dominio.lancamento import Lancamento

VENDA_BOA = Lancamento(cliente="Ana", descricao="Passagem GRU-LIS",
                       faturamento="5360", custo="4800", lucro="560")
VENDA_TORTA = Lancamento(cliente="Ana", descricao="x",
                         faturamento="5360", custo="4800", lucro="900")


class InterpretadorFalso:
    nome = "falso"

    def __init__(self, devolve=VENDA_BOA, erro=None):
        self.devolve = devolve
        self.erro = erro
        self.textos = []

    def interpretar(self, texto):
        self.textos.append(texto)
        if self.erro:
            raise RuntimeError(self.erro)
        return self.devolve


class DestinoFalso:
    nome = "planilha"

    def __init__(self, erro=None):
        self.escreveu = []
        self._erro = erro

    def escrever(self, lanc):
        if self._erro:
            raise RuntimeError(self._erro)
        self.escreveu.append(lanc)
        return ResultadoEscrita(destino=self.nome, referencia="linha 3")


def montar(interpretador=None, autorizados="42", destino=None):
    destino = destino or DestinoFalso()
    conversa = Conversa(interpretador or InterpretadorFalso(), [destino],
                        Config(autorizados=autorizados))
    return conversa, destino


def msg(texto, de=42, chat=42):
    return Mensagem(de=de, conversa=chat, texto=texto)


def test_quem_nao_esta_na_lista_e_ignorado_em_silencio():
    """Silencio, nao recusa: responder confirma para um estranho que o bot existe."""
    conversa, destino = montar()
    assert conversa.receber(msg("vendi 5360", de=999)) is None
    assert destino.escreveu == []


def test_mensagem_sem_valor_recebe_ajuda_e_nao_vai_pro_modelo():
    """Sem este filtro, 'bom dia' viraria um resumo sem sentido -- e custaria uma
    chamada de API."""
    interpretador = InterpretadorFalso()
    conversa, _ = montar(interpretador)
    resposta = conversa.receber(msg("bom dia"))
    assert "conta a venda" in resposta.lower()
    assert interpretador.textos == []


def test_venda_boa_volta_como_resumo_e_nao_grava_ainda():
    conversa, destino = montar()
    resposta = conversa.receber(msg("vendi pra Ana por 5360, custou 4800"))
    assert "Ana" in resposta
    assert "R$ 5.360,00" in resposta
    assert "R$ 560,00" in resposta
    assert destino.escreveu == []


def test_sim_grava_e_devolve_a_referencia():
    conversa, destino = montar()
    conversa.receber(msg("vendi pra Ana por 5360, custou 4800"))
    resposta = conversa.receber(msg("sim"))
    assert destino.escreveu == [VENDA_BOA]
    assert "linha 3" in resposta


def test_nao_cancela_sem_gravar():
    conversa, destino = montar()
    conversa.receber(msg("vendi 5360 custo 4800"))
    resposta = conversa.receber(msg("não"))
    assert destino.escreveu == []
    assert "cancel" in resposta.lower()


def test_correcao_reinterpreta_com_a_mensagem_original_junto():
    interpretador = InterpretadorFalso()
    conversa, _ = montar(interpretador)
    conversa.receber(msg("vendi 5360 custo 4800"))
    conversa.receber(msg("o cliente e Bruno"))
    assert "vendi 5360 custo 4800" in interpretador.textos[-1]
    assert "Bruno" in interpretador.textos[-1]


def test_conta_que_nao_fecha_nao_grava_nem_com_sim():
    """A trava e o ponto do robo: com margem de 5-6%, gravar errado vira prejuizo."""
    conversa, destino = montar(InterpretadorFalso(devolve=VENDA_TORTA))
    resumo = conversa.receber(msg("vendi 5360 custo 4800 lucro 900"))
    assert "nao fecha" in resumo.lower()
    resposta = conversa.receber(msg("sim"))
    assert destino.escreveu == []
    assert "correcao" in resposta.lower()


def test_erro_do_modelo_vira_recado_e_nao_derruba():
    conversa, _ = montar(InterpretadorFalso(erro="quota esgotada"))
    assert "quota esgotada" in conversa.receber(msg("vendi 5360"))


def test_cada_conversa_tem_a_sua_pendencia():
    """Duas pessoas falando com o robo nao podem se misturar."""
    conversa, destino = montar(autorizados="42,43")
    conversa.receber(msg("vendi 5360 custo 4800", de=42, chat=42))
    resposta = conversa.receber(msg("sim", de=43, chat=43))
    assert "conta a venda" in resposta.lower()
    assert destino.escreveu == []


def test_destino_que_falha_avisa_e_nao_finge_que_gravou():
    conversa, _ = montar(destino=DestinoFalso(erro="planilha fora do ar"))
    conversa.receber(msg("vendi 5360 custo 4800"))
    resposta = conversa.receber(msg("sim"))
    assert "planilha fora do ar" in resposta


def test_depois_de_gravar_a_proxima_mensagem_comeca_do_zero():
    """Sem limpar a pendencia, o proximo 'sim' regravaria a venda anterior."""
    conversa, destino = montar()
    conversa.receber(msg("vendi 5360 custo 4800"))
    conversa.receber(msg("sim"))
    resposta = conversa.receber(msg("sim"))
    assert len(destino.escreveu) == 1
    assert "conta a venda" in resposta.lower()


def test_duas_pessoas_no_mesmo_grupo_nao_se_misturam():
    """Num grupo com dois vendedores, o 'sim' de um nao pode confirmar o resumo
    do outro. A pendencia e por pessoa, nao por conversa."""
    conversa, destino = montar(autorizados="42,43")
    conversa.receber(msg("vendi 5360 custo 4800", de=42, chat=77))
    resposta = conversa.receber(msg("sim", de=43, chat=77))
    assert destino.escreveu == []
    assert "conta a venda" in resposta.lower()


def test_correcao_de_um_nao_entra_na_venda_do_outro():
    interpretador = InterpretadorFalso()
    conversa, _ = montar(interpretador, autorizados="42,43")
    conversa.receber(msg("vendi 5360 custo 4800", de=42, chat=77))
    conversa.receber(msg("vendi 9000 custo 8000", de=43, chat=77))
    assert "5360" not in interpretador.textos[-1]


def test_destino_fora_do_ar_guarda_o_resumo_para_nova_tentativa():
    """Jogar a pendencia fora obrigaria a pessoa a digitar a venda inteira de
    novo, por um problema que nao foi dela."""
    destino = DestinoFalso(erro="planilha fora do ar")
    conversa, _ = montar(destino=destino)
    conversa.receber(msg("vendi 5360 custo 4800"))
    resposta = conversa.receber(msg("sim"))
    assert "sim de novo" in resposta

    destino._erro = None
    assert "linha 3" in conversa.receber(msg("sim"))
    assert len(destino.escreveu) == 1


def test_resumo_esquecido_vence(monkeypatch):
    """Um 'ok' mandado horas depois, por outro motivo, nao pode gravar a venda
    de ontem."""
    import app.conversa as mod
    agora = [1000.0]
    monkeypatch.setattr(mod.time, "monotonic", lambda: agora[0])

    conversa, destino = montar()
    conversa.receber(msg("vendi 5360 custo 4800"))
    agora[0] += mod.VALIDADE_SEGUNDOS + 1
    resposta = conversa.receber(msg("ok"))

    assert destino.escreveu == []
    assert "conta a venda" in resposta.lower()
