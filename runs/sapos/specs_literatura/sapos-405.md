## Resumo
Criar uma variável `reply_to` para definir um endereço de resposta nos emails automáticos enviados pelo SAPOS.

## Descrição
O SAPOS envia emails automáticos. Hoje, quando alguém responde a um desses emails, a resposta se perde. A proposta é permitir configurar um endereço de email de _reply_to_ para esses envios.

## Versão do produto
Não informado na issue original.

## Justificativa
Quando uma pessoa responde a um email automático do SAPOS, a resposta não chega a ninguém. Com um endereço de _reply_to_ configurado, as respostas iriam para um destinatário definido.

## Caso de uso ou cenário
1. O SAPOS envia um email automático a uma pessoa.
2. A pessoa responde a esse email.
3. Situação atual: a resposta se perde.
4. Situação desejada: a resposta vai para o endereço de _reply_to_ configurado.

## Possível solução
A issue sugere criar uma variável `reply_to`, configurável na tela de variáveis do SAPOS. O valor dessa variável seria usado como endereço de resposta nos emails automáticos.