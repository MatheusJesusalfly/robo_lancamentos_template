# Instruções para o Claude neste projeto

Este é um robô-modelo: ele lê a venda pelo Telegram, confere a conta, pede
confirmação e grava a linha numa planilha do Google. Ele foi feito para ser
**adaptado** por quem baixou, e quem baixou provavelmente é dono ou dona de uma
agência de viagens, **não uma pessoa técnica**.

## A primeira coisa, antes de qualquer outra

Abra `manual/MANUAL.md`. **Se ele ainda estiver com os colchetes do modelo
(`[Cole aqui...]`), a regra de negócio da pessoa ainda não existe.**

Nesse caso, antes de ler código, antes de responder pergunta técnica e antes de
propor qualquer mudança, diga isto e comece a entrevista:

> "Antes de mexer em qualquer coisa eu preciso entender como funciona a sua
> agência. São oito perguntas, uma de cada vez. No fim eu escrevo o manual e
> você confere."

As perguntas e como conduzir estão em `.claude/skills/entrevista/SKILL.md`.
Siga aquele arquivo à risca, inclusive a ordem.

## Como falar com quem está do outro lado

- **Português de gente.** Nunca diga *prompt*, *API*, *endpoint*, *commit* ou
  *refatorar* sem a pessoa usar a palavra primeiro.
- **Uma pergunta por vez.** Duas perguntas juntas travam quem não é técnico.
- **Não peça para ela abrir arquivo.** Você abre, você edita, você mostra o
  resultado em texto.
- **Nunca diga que está pronto sem ter rodado os testes.**

## Arquivos que ela não consegue ver

`.env`, `.env.example`, `.gitignore` e a pasta `.claude/` começam com ponto, e
por isso são **invisíveis** no Finder e no Explorer. Nunca peça para ela "abrir
o `.env.example`" ou "copiar o arquivo": ela não vai achar.

Quando for preciso configurar, **faça você**: crie o `.env`, peça cada valor
por mensagem ("me manda o token que o BotFather te deu"), escreva no arquivo e
confirme em texto o que ficou lá — sem repetir o valor da chave na tela.

## Depois de qualquer mudança no código

Rode `.venv/bin/pytest -q` e diga o resultado em uma frase simples:
verde significa que o robô continua fazendo o que fazia; vermelho significa
que a mudança quebrou alguma coisa e você vai consertar antes de continuar.

Esta é a única proteção que a pessoa tem: ela não consegue ler o que você
mudou. **Nunca entregue com teste vermelho.**

## Onde mexer, e onde não

| Ela pediu | Você mexe em |
|---|---|
| "quero mudar como o robô entende a venda" | `manual/MANUAL.md` — quase sempre é só isso |
| "quero mandar pro meu CRM" | nova classe ao lado de `app/destino/planilha.py`, seguindo `app/destino/porta.py` |
| "quero no WhatsApp" | nova classe ao lado de `app/canal/telegram.py`. Avise que aí precisa de servidor com endereço público — é outro degrau |
| "não quero o Google lendo meus dados" | `app/interpretador/`, e explique o plano pago |
| um campo novo na venda | **cinco lugares, todos os cinco:** `app/dominio/lancamento.py`, o `ESQUEMA` em `app/interpretador/gemini.py`, o dicionário `corpo` em `app/destino/planilha.py`, o `resumir()` em `app/conversa.py`, e `apps_script/Codigo.gs`. Esquecer o `corpo` faz a coluna nova chegar vazia na planilha — **com os testes verdes**, que é a única proteção que ela tem |

**O manual é a primeira resposta.** Antes de propor mudar código, pergunte-se
se escrever a regra em `manual/MANUAL.md` já resolve. Quase sempre resolve.

## Regras duras

- **Chave e token só no `.env`.** Nunca em `.py`, `.md`, teste ou mensagem de
  commit. O `.env` está no `.gitignore` e continua lá.
- **Não invente número.** Se a conta não fecha, o robô pergunta — não conserta
  sozinho. Essa é a razão de ele existir.
- **Não acrescente dependência** sem dizer por quê. São quatro hoje, de
  propósito: cada uma é mais uma coisa que pode quebrar na máquina dela.
