# Como este robô funciona

Escrito para quem vai **mudar** o robô — você, e o Claude trabalhando com você.
Não precisa saber programar para ler isto.

## O caminho de uma venda

1. **Chega uma mensagem** no Telegram (`app/canal/telegram.py`).
2. **É de alguém autorizado?** Se não estiver na lista do `.env`, o robô fica
   calado. Silêncio, não recusa — responder já entregaria a um estranho que o
   bot existe (`app/config.py`).
3. **Parece uma venda?** Se não tem nenhum valor em dinheiro na mensagem, ele
   responde explicando como se usa, e não gasta uma chamada do modelo
   (`app/conversa.py`).
4. **O modelo lê** a mensagem junto com o **seu** `manual/MANUAL.md` e devolve
   os dados da venda (`app/interpretador/gemini.py`).
5. **A conta fecha?** Faturamento menos custo tem de dar o lucro. Se não dá, o
   robô mostra o problema e **não grava**, nem se você disser sim
   (`app/dominio/validacao.py`).
6. **Você confirma.** Só depois do `sim` ele grava.
7. **Grava na planilha** e responde com o número da linha
   (`app/destino/planilha.py`).

## As três portas

O robô tem três peças trocáveis, e uma regra de negócio no meio que não conhece
nenhuma das três.

```
   Telegram            Gemini            Planilha
  (a entrada)        (o modelo)         (o destino)
       │                  │                  │
       └────────→ [ a regra de negócio ] ────┘
              não conhece nenhum dos três
```

Cada porta é um arquivo chamado `porta.py`, e ele descreve o contrato que
qualquer substituto precisa cumprir:

| Porta | O contrato | A implementação que veio |
|---|---|---|
| Entrada | `app/canal/porta.py` | `telegram.py` |
| Modelo | `app/interpretador/porta.py` | `gemini.py` |
| Destino | `app/destino/porta.py` | `planilha.py` |

**Trocar uma porta é escrever uma classe nova, não mexer na regra de negócio.**
As receitas estão em [`RECEITAS.md`](RECEITAS.md).

## O manual é o robô

`manual/MANUAL.md` entra no prompt do modelo toda vez que uma venda chega.

Isso significa que **a maior parte das mudanças que você quer não é mudança de
código**: é escrever a regra naquele arquivo, em português.

- *"ele tem que entender que quando o cliente paga direto o fornecedor só entra
  a comissão"* → é manual.
- *"quero que ele grave no meu CRM"* → é código (uma porta nova).

Na dúvida, tente o manual primeiro.

## Por que ele para tanto

Três decisões deliberadas, e vale conhecê-las antes de removê-las:

- **Nunca grava sem confirmação.** Numa agência a margem fica em 5-6%: um custo
  errado é o lucro inteiro, e quem enxerga o erro é quem vendeu, olhando o
  resumo antes — não a planilha depois.
- **Trava quando a conta não fecha**, em vez de chutar. Chutar grava um número
  errado com cara de conferido, que é pior do que não gravar.
- **Só obedece a quem está na lista.** Lista vazia significa ninguém, não todo
  mundo.

## Os arquivos

| Onde | O quê |
|---|---|
| `manual/MANUAL.md` | **A sua regra de negócio. É o robô.** |
| `app/config.py` | O que vem do `.env`, e quem pode lançar |
| `app/dinheiro.py` | Lê e escreve valores em reais, sempre exatos |
| `app/dominio/` | O que é uma venda, e quando a conta fecha |
| `app/canal/` · `app/interpretador/` · `app/destino/` | As três portas |
| `app/conversa.py` | Resumo, confirmação e correção |
| `app/__main__.py` | Liga tudo e fica ouvindo |
| `apps_script/Codigo.gs` | O que vai colado na sua planilha |
| `tests/` | O cinto de segurança |

## O cinto de segurança

```bash
.venv/bin/pytest
```

Depois de **toda** mudança. Verde: o robô continua fazendo o que fazia.
Vermelho: quebrou, conserta antes de usar.

Você não precisa saber ler código para confiar no robô. Precisa saber olhar
essa cor.
