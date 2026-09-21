# Comece aqui

Se você está lendo isto, baixou a pasta do robô. São três passos.

## 1. Abra o Claude Code nesta pasta e cole isto

```
Leia o CLAUDE.md desta pasta e me entreviste para montar o manual da minha
agência. Eu não sou técnico: me faça uma pergunta por vez, em português
simples, e no fim me mostre o manual para eu confirmar.
```

São oito perguntas, uns doze minutos. No fim, `manual/MANUAL.md` vai estar
escrito com as suas palavras — e **esse arquivo é o robô**. Tudo que estiver
escrito nele é como o robô vai entender as suas vendas.

## 2. Deixe o Claude te guiar pela configuração

**Não tente seguir o README sozinho.** Peça a ele, na mesma conversa:

```
Me guia pelos seis minutos de clique do README, um passo por vez. Eu vou
clicando e te trazendo o que aparecer na tela. No fim, cria o .env com tudo.
```

Ele dá um passo, você clica, volta e cola o que apareceu, ele guarda. São
quatro coisas e **nenhuma pede cartão de crédito**:

- o token do bot (BotFather, no Telegram)
- o seu id no Telegram (@userinfobot)
- a chave do Google AI Studio
- a URL da sua planilha (Apps Script)

**Numa delas o Google vai mostrar uma tela dizendo que "este app não foi
verificado", e só oferecer Cancelar.** É normal: o app não verificado é o seu
próprio script, na sua própria planilha. O caminho é *Avançado → Acessar*, uma
vez só. O `README.md` explica com calma, e o Claude também.

A regra que vale para tudo daqui em diante: **você não precisa decorar nada.
Pergunta.**

## 3. Ligue

```
.venv/bin/python -m app
```

Mande uma venda pro seu bot no Telegram. Ele devolve o resumo. Você responde
`sim`. A linha aparece na planilha.

---

## Depois, é só conversar

Quer mudar alguma coisa? Fale em português com o Claude nesta pasta:

- *"o robô tem que perguntar o localizador também"*
- *"quando o cliente paga direto o fornecedor, só entra a comissão"*
- *"quero que grave no meu CRM em vez da planilha"*

**Depois de cada mudança ele roda os testes.** Se der verde, o robô continua
funcionando. Se der vermelho, alguma coisa quebrou e ele conserta antes de
devolver. É o seu cinto de segurança: você não precisa saber ler o código.

## Um aviso que não é firula

O robô vem configurado com o **plano gratuito** do Gemini. Nele, o Google pode
usar o que passa pelo robô para treinar os produtos dele, e revisores humanos
podem ler.

Para aprender e testar, tudo bem. **Antes de apontar para venda de cliente de
verdade**, peça ao Claude: *"quero trocar para o plano pago, o Google não pode
ler meus dados"*. É uma mudança pequena — o robô foi feito para isso.
