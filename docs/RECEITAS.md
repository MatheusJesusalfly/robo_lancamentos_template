# Receitas

As mudanças que mais se pede, com o passo a passo. **Peça em português ao
Claude** dentro desta pasta — ele segue estas receitas.

Depois de qualquer uma delas: `.venv/bin/pytest`. Se ficar vermelho, a mudança
quebrou algo e tem de ser consertada antes de usar.

---

## Mudar como o robô entende as vendas

**Quase sempre é isto, e não é código.** Edite `manual/MANUAL.md`.

Exemplos que são manual, não código:

- "quando o cliente paga direto o fornecedor, só entra a comissão"
- "taxa de cartão é custo, não desconto no faturamento"
- "se vier sem o nome do cliente, pergunta em vez de inventar"
- "incentivo de operadora soma no lucro mas não no faturamento"

Escreva com as suas palavras. Não precisa ficar bonito; precisa ficar
verdadeiro.

---

## Acrescentar um campo à venda

Exemplo: o localizador, ou a data de embarque.

São **cinco lugares**, e esquecer qualquer um faz a coluna chegar vazia na
planilha — com os testes verdes:

1. `app/dominio/lancamento.py` — o campo novo no modelo.
2. `app/interpretador/gemini.py` — o campo no `ESQUEMA` (e em `required` se for
   obrigatório).
3. `app/destino/planilha.py` — o campo no dicionário `corpo`. **É este que de
   fato viaja.**
4. `app/conversa.py` — o campo em `resumir()`, para você ver antes de confirmar.
5. `apps_script/Codigo.gs` — a coluna nova no `appendRow`, e **reimplantar** o
   Apps Script (Implantar → Gerenciar implantações → editar → Nova versão).

---

## Gravar no meu CRM em vez da planilha

1. Crie `app/destino/<nome>.py` com uma classe que tenha `nome` e um método
   `escrever(lanc)` devolvendo `ResultadoEscrita`. O contrato está em
   `app/destino/porta.py`. **Não precisa herdar de nada.**
2. Em `app/__main__.py`, passe a sua classe em `destinos=[...]`.
3. As credenciais do CRM vão no `.env` e em `app/config.py`. **Nunca no código.**

Dá para manter os dois: `destinos=[Planilha(...), MeuCRM(...)]`. Se um falhar, o
outro ainda grava, e o robô avisa o que não entrou.

---

## Trocar o Telegram pelo WhatsApp

Funciona igual — mas **muda o seu custo de vida**, e vale saber antes.

O Telegram busca as mensagens sozinho, então o robô roda no seu computador,
atrás de qualquer wi-fi. O WhatsApp precisa de um **servidor com endereço
público ligado o tempo todo**, mais um serviço que converse com o WhatsApp
(Evolution API, por exemplo), mais um número dedicado.

A parte do código é pequena: uma classe em `app/canal/` com `receber()` e
`responder()`, seguindo `app/canal/porta.py`. A parte de infraestrutura é o
degrau de cima.

---

## O Gemini está dando 503, ou demorando demais

Sintoma, na conversa do Telegram:

```
Nao consegui entender essa venda: o Gemini recusou (503):
This model is currently experiencing high demand
```

ou

```
Nao consegui entender essa venda: a chamada nao completou: ... timed out
```

**Primeiro: o robô já tenta três vezes sozinho.** Se a mensagem terminar com
*"tentei 3 vezes"*, as três falharam — não foi desistência na primeira. Se ela
**não** terminar assim, foi outro problema, e não é este o caso aqui.

O plano gratuito é uma fila, e quando o modelo que você escolheu está cheio, os
"lite" costumam continuar respondendo. **Troque o modelo:**

1. Abra o `.env` (ou peça ao Claude: *"troca o modelo do Gemini"*).
2. Mude `GEMINI_MODELO` para outro da lista abaixo.
3. Reinicie o robô: `Ctrl+C`, e `.venv/bin/python -m app` de novo.

| Modelo | Como se comportou |
|---|---|
| `gemini-3.5-flash-lite` | **O padrão do kit.** Respondeu em ~1,2s numa hora em que os outros dois davam 503 |
| `gemini-3.5-flash` | Bom, mas foi o que mais pegou fila |
| `gemini-3.6-flash` | Idem |
| `gemini-2.5-flash` | **Não use.** Numa chave criada hoje, responde 404 — não existe mais nela |

## O robô diz "o Gemini recusou (404)"

O nome do modelo no `.env` não existe na sua chave. Acontece porque **a lista de
modelos muda com o tempo** — um nome que funcionava some.

Abra **aistudio.google.com**, veja quais modelos aparecem para a sua chave, e
ponha um deles em `GEMINI_MODELO`. Comece pelo que termina em `-lite`.

Não é erro da sua instalação e não tem nada a ver com a sua chave estar certa ou
errada — chave errada dá **401**, não 404.

## Sair do plano gratuito do Gemini

Faça isto **antes de apontar o robô para venda de cliente de verdade.**

No plano gratuito, os termos do Google dizem que o que passa pelo robô pode ser
usado para melhorar os produtos deles e que revisores humanos podem ler.
Mensagem de venda tem nome de cliente.

- **Mais simples:** ative o faturamento no Google AI Studio. A mesma chave passa
  a valer como plano pago e nada no código muda.
- **Trocar de modelo:** crie `app/interpretador/<nome>.py` com um método
  `interpretar(texto)` que devolve um `Lancamento`, seguindo
  `app/interpretador/porta.py`, e troque em `app/__main__.py`.

---

## Mais de uma pessoa lançando

Ponha os ids do Telegram separados por vírgula em `AUTORIZADOS`, no `.env`.
Cada pessoa descobre o dela falando com **@userinfobot**.

Cada uma tem a sua própria conversa em andamento, mesmo num grupo: o `sim` de
uma nunca confirma a venda da outra.

---

## O robô esqueceu o resumo

É de propósito, em dois casos:

- **Ele reiniciou.** A memória é da execução. Para não esquecer, o resumo
  precisaria de um banco de dados — é o degrau de cima.
- **Passaram 30 minutos.** Um "ok" mandado horas depois, por outro motivo, não
  pode gravar a venda de ontem.

Nos dois casos, é só mandar a venda de novo.
