"""A conversa: resumo, confirmacao, e so entao escrita.

O robo nunca grava sem alguem dizer "sim". Nao e cerimonia: numa agencia com
margem de 5-6%, um custo errado vira prejuizo, e quem enxerga o erro e quem
vendeu -- olhando o resumo ANTES, nao a planilha depois.

A pendencia e por PESSOA dentro da conversa, nao por conversa. Num grupo com
dois vendedores isso e a diferenca entre funcionar e gravar a venda errada: o
"sim" de um nao pode confirmar o resumo do outro.

Um resumo esquecido tambem vence. Sem isso, um "ok" mandado horas depois por
outro motivo gravaria a venda de ontem.

A memoria e da execucao. Se o robo reiniciar, ele esquece o resumo que esperava
confirmacao. Para uma aula esta otimo; para valer, e a primeira coisa que vira
banco.
"""

from __future__ import annotations

import logging
import re
import time

from app.canal.porta import Mensagem
from app.config import Config
from app.destino.porta import Destino, escrever_em
from app.dinheiro import em_reais
from app.dominio.lancamento import Lancamento
from app.dominio.validacao import conferir
from app.interpretador.porta import Interpretador

log = logging.getLogger("robo")

AJUDA = ("Me conta a venda que voce fechou: cliente, o que foi vendido, quanto "
         "entrou e quanto custou. Eu monto o resumo e so gravo depois que voce "
         "disser sim.")

SIM = {"sim", "s", "isso", "ok", "confirma", "confirmo", "pode", "pode gravar"}
NAO = {"nao", "não", "n", "cancela", "cancelar", "esquece", "deixa"}

#: Tem algum valor em dinheiro na mensagem? Sem isto, "bom dia" iria para o
#: modelo e voltaria como um resumo sem sentido -- e custaria uma chamada.
_TEM_VALOR = re.compile(r"\d[\d.]*,\d{2}|R\$\s*\d|\d{3,}")

#: Meia hora. Passou disso, o resumo esquecido nao vale mais nada.
VALIDADE_SEGUNDOS = 30 * 60


def resumir(lanc: Lancamento, problemas: list[str]) -> str:
    linhas = [
        f"Cliente: {lanc.cliente}",
        f"O que: {lanc.descricao}",
        f"Entrou: {em_reais(lanc.faturamento)}",
        f"Custou: {em_reais(lanc.custo)}",
        f"Sobrou: {em_reais(lanc.lucro)}",
    ]
    if lanc.observacao:
        linhas.append(f"Obs: {lanc.observacao}")
    linhas.append("")
    if problemas:
        linhas.append("Nao da para gravar assim:")
        linhas += [f"- {p}" for p in problemas]
        linhas.append("")
        linhas.append("Me manda a correcao.")
    else:
        linhas.append("Gravo? Responde sim.")
    return "\n".join(linhas)


class Conversa:
    def __init__(self, interpretador: Interpretador, destinos: list[Destino],
                 config: Config):
        self._interpretador = interpretador
        self._destinos = destinos
        self._config = config
        #: (conversa, quem) -> (quando, texto acumulado, lancamento montado)
        self._pendentes: dict[tuple[int, int], tuple[float, str, Lancamento]] = {}

    def receber(self, msg: Mensagem) -> str | None:
        """O que responder, ou None para ficar calado de proposito."""
        if not self._config.pode_lancar(msg.de):
            log.info("ignorando %s: fora da lista", msg.de)
            return None

        texto = msg.texto.strip()
        baixo = texto.lower()
        chave = (msg.conversa, msg.de)
        pendente = self._pendentes.get(chave)

        if pendente and time.monotonic() - pendente[0] > VALIDADE_SEGUNDOS:
            self._pendentes.pop(chave)
            pendente = None

        if pendente:
            if baixo in SIM:
                return self._gravar(chave)
            if baixo in NAO:
                self._pendentes.pop(chave)
                return "Cancelado. Nada foi gravado."
            # Qualquer outra coisa e correcao, e vai junto com o texto original:
            # sozinha, "o cliente e Bruno" nao diz ao modelo de que venda se fala.
            return self._montar(chave, f"{pendente[1]}\n\nCorrecao: {texto}")

        if not _TEM_VALOR.search(texto):
            return AJUDA

        return self._montar(chave, texto)

    def _montar(self, chave: tuple[int, int], texto: str) -> str:
        try:
            lanc = self._interpretador.interpretar(texto)
        except Exception as erro:
            log.warning("interpretacao falhou: %s", erro)
            return f"Nao consegui entender essa venda: {erro}"

        self._pendentes[chave] = (time.monotonic(), texto, lanc)
        return resumir(lanc, conferir(lanc))

    def _gravar(self, chave: tuple[int, int]) -> str:
        _, _, lanc = self._pendentes[chave]

        # Confere de novo na hora de gravar. E aqui que a trava vale: o "sim"
        # nao autoriza gravar uma conta que nao fecha.
        problemas = conferir(lanc)
        if problemas:
            return resumir(lanc, problemas)

        resultados = escrever_em(self._destinos, lanc)
        gravados = [r for r in resultados if not r.pendencias]
        falhas = [p for r in resultados for p in r.pendencias]

        # A pendencia so morre se algo entrou. Se a planilha estava fora do ar,
        # jogar fora o resumo obrigaria a pessoa a digitar a venda de novo --
        # por um problema que nao foi dela.
        if gravados:
            self._pendentes.pop(chave)

        if not gravados:
            return ("Nao consegui gravar:\n"
                    + "\n".join(f"- {f}" for f in falhas)
                    + "\n\nO resumo continua aqui. Responde sim de novo para tentar outra vez.")

        linhas = [f"Gravado: {r.destino}, {r.referencia}" for r in gravados]
        if falhas:
            linhas.append("Nao entrou em:")
            linhas += [f"- {f}" for f in falhas]
        return "\n".join(linhas)
