---
name: entrevista
description: Use quando alguem quiser adaptar este robo para a propria agencia - conduz as 8 perguntas que arrancam a regra de negocio e preenche manual/MANUAL.md
---

# Entrevista da agência

Você vai entrevistar o dono ou a dona de uma agência de viagens para descobrir a
regra de negócio dele, e escrever `manual/MANUAL.md` a partir das respostas.

Quem está do outro lado **não é uma pessoa técnica**. Ela sabe de cor como a
agência dela ganha dinheiro, e não sabe nada de código. A entrevista inteira
acontece no terreno dela.

## Como conduzir

- **Uma pergunta por vez.** Espere a resposta antes da próxima.
- **Não explique tecnologia.** Ninguém aqui precisa saber o que é um prompt.
- **Não aceite resposta vaga nas perguntas 3, 4 e 5.** São as que valem. Se a
  pessoa responder "depende", pergunte "depende do quê?" até ter a regra.
- **Doze minutos.** Se apertar, corte a 7 — nunca a 3, a 4 ou a 5.
- **A regra do "fica para depois":** quando aparecer a exceção complicada, e vai
  aparecer, escreva na seção "Fica para depois" do manual e siga em frente. O
  manual cresce primeiro; o robô cresce depois.

## As oito perguntas

1. **Quando uma venda fecha hoje, quem escreve, onde, e quantas vezes a mesma
   informação é digitada?**
2. **Me mostra uma mensagem de venda de verdade, como ela chega hoje.**
3. **Nessa venda: quanto entrou, quanto saiu, e quanto sobrou para você? Como
   você chegou nesse número?**
4. **Tem mais de um jeito de vender? Descreve cada um.**
5. **O que entra na conta e é fácil esquecer?**
6. **Qual informação, se vier errada, te custa dinheiro?**
7. **Quem pode lançar, e quem não pode?**
8. **Quando a venda está gravada, ela está pronta, ou alguém ainda confere?**

**A pergunta 2 é a âncora.** Tudo depois dela se pendura no exemplo concreto,
porque pessoa não técnica trava em pergunta abstrata e destrava em cima de uma
venda que ela mesma trouxe. Se ela não tiver uma à mão, peça que invente uma
parecida com as de verdade — mas insista em ter o exemplo antes de seguir.

**A pergunta 6 define onde o robô trava.** Numa agência a margem costuma ser de
5 a 6%: um custo errado não é um detalhe, é o lucro inteiro. O robô que chuta é
pior do que robô nenhum, porque grava um número errado com cara de conferido.

## No fim

1. Escreva `manual/MANUAL.md` com as respostas, na estrutura que o arquivo já
   tem. **Use as palavras da pessoa, não as suas.**
2. Mostre o manual e pergunte: *"é assim que funciona na sua agência?"*
3. Só depois de ela confirmar, diga que o robô já sabe ler as vendas dela — e
   que, daqui em diante, mudar o comportamento dele é editar esse texto.
4. Diga qual é o próximo passo: preencher o `.env` seguindo o `README.md`.
