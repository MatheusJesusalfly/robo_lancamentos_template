# Robô de lançamentos — modelo

Você manda a venda pelo Telegram. Ele entende, confere se a conta fecha,
devolve o resumo, e **só grava depois que você disser `sim`** — uma linha nova
na sua planilha do Google.

É um modelo para você adaptar à sua agência. Começa a adaptação em
[`COMECE_AQUI.md`](COMECE_AQUI.md).

Para entender ou mudar o robô depois:
[`docs/COMO_FUNCIONA.md`](docs/COMO_FUNCIONA.md) (o caminho de uma venda e as
três portas) e [`docs/RECEITAS.md`](docs/RECEITAS.md) (o passo a passo das
mudanças mais pedidas — trocar o destino, sair do plano gratuito, acrescentar
um campo).

---

## ⚠️ Antes de tudo: o plano gratuito do Gemini lê os seus dados

Este robô vem configurado com o **plano gratuito** do Google AI Studio, porque
assim ele não custa nada e não precisa de cartão de crédito.

Nos termos do serviço **não pago**, o Google pode usar o que você manda e o que
volta para melhorar os produtos dele, **revisores humanos podem ler o material**,
e o próprio Google pede que não se envie informação sensível, confidencial ou
pessoal por ali.

Mensagem de venda tem nome de cliente, valor e localizador.

- **Para aprender e testar:** tudo bem.
- **Para a sua operação de verdade:** troque antes para o plano pago, onde isso
  não se aplica. Peça ao Claude: *"quero trocar para o plano pago"*. É uma
  mudança pequena — o robô foi desenhado para isso.

---

## Os seis minutos de clique

Quatro coisas, e nenhuma pede cartão de crédito. Se travar em qualquer uma,
peça ao Claude nesta pasta: *"me ajuda a pegar o token do Telegram"*.

**1. O bot (1 min)** — no Telegram, fale com **@BotFather**, mande `/newbot`,
escolha um nome. Ele devolve um token parecido com `8123456789:AAF...`. Vai em
`TELEGRAM_TOKEN`.

**2. O seu id (30 s)** — fale com **@userinfobot** no Telegram. Ele responde com
um número. Vai em `AUTORIZADOS`. **Sem ninguém aqui o robô não obedece a
ninguém**, e isso é de propósito: um robô que escreve e não sabe a quem obedecer
é pior ligado do que desligado.

**3. A chave do modelo (2 min)** — em **aistudio.google.com**, *Get API key*.
Vai em `GEMINI_API_KEY`. (Leia o aviso lá em cima.)

> Aproveite que está lá e **confira a lista de modelos**. Nomes entram e saem:
> se o robô responder *"o Gemini recusou (404)"*, é porque o nome que está no
> `.env` não existe mais na sua chave. A receita para trocar está em
> [`docs/RECEITAS.md`](docs/RECEITAS.md).

**4. A planilha (3 min)** — crie uma planilha no Google Sheets. Vá em
**Extensões → Apps Script**, apague o que estiver lá e cole o conteúdo de
[`apps_script/Codigo.gs`](apps_script/Codigo.gs). Troque o `SEGREDO` por uma
palavra sua. Depois **Implantar → Nova implantação → App da Web**, executando
como você, com acesso para *qualquer pessoa*. Copie a URL para `PLANILHA_URL` e
a sua palavra para `PLANILHA_SEGREDO`.

> ### Vai aparecer uma tela dizendo que o app não foi verificado. É normal.
>
> Na primeira implantação o Google avisa que *"este app não foi verificado"* e
> oferece só o botão **Cancelar**. Não é um erro e não é perigo: o "app não
> verificado" **é o seu próprio script, na sua própria planilha**. O Google
> mostra esse aviso para todo script que a pessoa escreveu e ele não revisou —
> e ele não revisa scripts pessoais.
>
> O caminho é: clique em **Avançado** (embaixo, à esquerda) e depois em
> **Acessar (nome do projeto) (não seguro)**. Em seguida ele pede permissão
> para o script mexer nas suas planilhas — que é exatamente o que você quer que
> ele faça. Clique em **Permitir**.
>
> Isso acontece **uma vez só**. Depois disso nunca mais aparece.

> O segredo importa: "qualquer pessoa" significa qualquer pessoa mesmo. Sem ele,
> quem descobrir o endereço escreve linhas na sua planilha.

> **Confira a última linha depois de colar.** O editor do Apps Script às vezes
> engole a última linha do que você colou — e ela é uma `}` sozinha, que fecha o
> arquivo. Sem ela a implantação falha com *"Ocorreu um erro"*, que não diz o
> que houve; o erro de verdade aparece antes, no editor:
> *"SyntaxError: Unexpected end of input"*.
>
> Role até o fim do editor: **a última linha tem de ser uma `}` sozinha.** Se
> não for, digite uma.

## Rodar

Precisa de **Python 3.11 ou mais novo**.

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
cp .env.example .env      # preencha as quatro coisas acima

.venv/bin/python -m app
```

Se faltar alguma coisa no `.env`, ele diz **tudo que falta de uma vez** e não
sobe. Mande a venda pro seu bot no Telegram e veja a linha aparecer.

## O seu cinto de segurança

```bash
.venv/bin/pytest
```

**Rode isso depois de toda mudança que você pedir ao Claude.**

Verde: o robô continua fazendo o que fazia. Vermelho: a mudança quebrou alguma
coisa, e você pede para ele consertar antes de usar.

Você não precisa saber ler código para confiar no robô — precisa saber olhar
essa cor. É a única proteção real contra um robô que passa a calcular errado em
silêncio, e numa agência com margem de 5 a 6% errar o custo é perder o lucro
inteiro.

## As três portas

O robô é feito de três peças trocáveis e uma regra de negócio no meio que não
conhece nenhuma delas.

```
   Telegram            Gemini            Planilha
  (a entrada)        (o modelo)         (o destino)
       │                  │                  │
       └────────→ [ a regra de negócio ] ────┘
              não conhece nenhum dos três
```

| Porta | Onde | Trocar por |
|---|---|---|
| Entrada | `app/canal/porta.py` | WhatsApp, e-mail, formulário |
| Modelo | `app/interpretador/porta.py` | Gemini pago, Claude, outro |
| Destino | `app/destino/porta.py` | Bitrix, Monde, RD Station, o seu CRM |

**Trocar qualquer uma é escrever uma classe nova, não mexer na regra de
negócio.** Repare que `Planilha` não herda de `Destino`: basta ter os métodos
certos. Peça ao Claude: *"quero gravar no meu CRM em vez da planilha"*.

Trocar o Telegram pelo WhatsApp é a única que muda o seu custo de vida: WhatsApp
precisa de um servidor com endereço público ligado o tempo todo. O Telegram,
não — por isso ele está aqui.

## O que este robô não faz, de propósito

Cancelamento, parcelamento, moeda estrangeira, anexo de PDF, relatório, painel.

Nada disso é difícil de acrescentar. Mas cada um deles começa escrevendo a
regra em `manual/MANUAL.md` — e boa parte deles nem precisa de código novo
depois disso.

## Os arquivos

| Onde | O quê |
|---|---|
| `manual/MANUAL.md` | **A sua regra de negócio. É o robô.** |
| `app/dominio/` | O que é uma venda e quando a conta fecha |
| `app/canal/`, `app/interpretador/`, `app/destino/` | As três portas |
| `app/conversa.py` | Resumo, confirmação e correção |
| `apps_script/Codigo.gs` | O que vai colado na planilha |
| `tests/` | O cinto de segurança |
| `docs/` | Como funciona, e as receitas de mudança |
