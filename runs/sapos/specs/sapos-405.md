# Spec: Variável `reply_to` para e-mails automáticos do SAPOS

## Objetivo

Hoje, quando o SAPOS envia um e-mail automático e o destinatário responde, a resposta se perde, porque não há um endereço configurado para recebê-la.

**O que construir:** uma configuração de endereço de *reply-to* para os e-mails automáticos. Ela deve ser editável pela tela de variáveis do sistema, sem alterar código nem fazer deploy.

**Usuários:**
- **Administradores do SAPOS**, que configuram o endereço na tela de variáveis.
- **Destinatários dos e-mails automáticos** (alunos, professores etc.), cujas respostas devem chegar a uma caixa monitorada.

**Histórias de usuário:**
- Como administrador, quero definir na tela de variáveis um e-mail de *reply-to* para que as respostas aos e-mails automáticos cheguem a uma caixa que alguém acompanha.
- Como destinatário de um e-mail automático, quero que, ao clicar em "Responder", minha mensagem vá para um endereço válido e monitorado.

## Premissas

1. "Tela de variáveis" é uma tela já existente no SAPOS para gerenciar variáveis de configuração. A nova variável deve seguir o mesmo mecanismo de cadastro e leitura das variáveis existentes.
2. O pedido é definir o cabeçalho `Reply-To`, e não o remetente (`From`). O título fala em "escolha de um remetente", mas o corpo da issue descreve claramente o problema das respostas.
3. A variável é única e global, e vale para todos os e-mails automáticos do sistema. Não há um valor por tipo de notificação.
4. Se a variável estiver vazia ou ausente, o comportamento atual se mantém: nenhum `Reply-To` é adicionado. Não deve haver erro nem bloqueio de envio.
5. A variável aceita um único endereço de e-mail.
6. Todos os pontos de envio de e-mail automático passam por um mecanismo comum, ou podem ser alterados para ler a variável.
7. O nome da variável será `reply_to`, conforme o título da issue.

## Stack Tecnológica

Não informado na issue original. A linguagem, o framework, o mecanismo de envio de e-mails e a forma de armazenar as variáveis precisam ser confirmados no repositório.

## Comandos

Não informado na issue original. Os comandos de build, teste, lint e servidor de desenvolvimento são desconhecidos.

## Estrutura do Projeto

Não informado na issue original. São desconhecidas:
- a localização do código de envio de e-mails (mailers, notificações);
- a localização do modelo e da tela de variáveis;
- a localização dos testes;
- a localização de seeds e migrações, caso as variáveis sejam criadas por esse meio.

## Estilo de Código

Não informado na issue original. Deve-se seguir as convenções já usadas no código existente de variáveis e de mailers.

## Estratégia de Testes

Não informado na issue original quanto a framework e localização. Os testes devem cobrir no mínimo:
- **Unitário/mailer, com a variável preenchida:** o e-mail automático gerado contém o cabeçalho `Reply-To` com o valor configurado.
- **Unitário/mailer, com a variável vazia ou ausente:** o e-mail é gerado sem `Reply-To` e sem erro, como no comportamento atual.
- **Cobertura dos pontos de envio:** todos os tipos de e-mail automático existentes respeitam a variável.
- **Tela de variáveis:** a variável `reply_to` aparece na tela e pode ser editada e salva. Se houver validação de formato, ela deve ser testada.

## Limites

- **Sempre:**
  - manter compatibilidade com instalações existentes, sem quebrar o envio quando a variável não estiver definida;
  - seguir o padrão existente de variáveis do sistema;
  - executar a suíte de testes antes de commitar.
- **Perguntar antes:**
  - alterar o remetente (`From`) dos e-mails;
  - mudar o esquema do banco de dados além do mínimo necessário para registrar a variável;
  - adicionar dependências;
  - criar uma configuração por tipo de e-mail em vez de uma global.
- **Nunca:**
  - commitar credenciais ou configurações reais de SMTP;
  - remover ou desabilitar testes existentes;
  - alterar o comportamento de envio de quem não configurar a variável.

## Critérios de Sucesso

1. Existe a variável `reply_to`, que é visível e editável na tela de variáveis do SAPOS.
2. Com `reply_to` preenchida, todos os e-mails automáticos enviados pelo SAPOS contêm o cabeçalho `Reply-To` com o endereço configurado.
3. Ao responder um e-mail automático em um cliente de e-mail comum, a resposta é endereçada ao valor de `reply_to`.
4. Com `reply_to` vazia ou inexistente, os e-mails são enviados exatamente como antes, sem cabeçalho `Reply-To` e sem erros.
5. Uma alteração do valor na tela de variáveis passa a valer nos envios seguintes, sem reiniciar a aplicação. Isso depende de confirmação, ver as Perguntas em Aberto.
6. Instalações existentes recebem a variável, vazia ou com valor padrão, sem intervenção manual, por exemplo via migração ou seed. A estratégia exata depende do mecanismo atual.
7. Os testes descritos na Estratégia de Testes passam.

## Perguntas em Aberto

1. **Reply-To ou remetente?** O título fala em "escolha de um remetente", mas a descrição trata das respostas. O objetivo é apenas o `Reply-To`, ou também tornar o `From` configurável?
2. **Escopo dos e-mails:** a variável deve valer para todos os e-mails automáticos, ou só para alguns tipos de notificação? Existem e-mails que não devem ter `Reply-To`, como redefinição de senha?
3. **Granularidade:** basta uma variável global, ou deve haver valores diferentes por tipo de e-mail ou por programa?
4. **Múltiplos endereços:** a variável deve aceitar mais de um endereço, separados por vírgula?
5. **Validação:** a tela de variáveis deve validar o formato de e-mail ao salvar? Ela já suporta validação por tipo de variável?
6. **Valor padrão:** a variável deve vir vazia, ou com algum padrão, por exemplo o mesmo endereço do remetente atual?
7. **Mecanismo de variáveis:** como as variáveis são criadas hoje (migração, seed, cadastro manual)? Elas são lidas a cada envio, ou ficam em cache?
8. **Documentação:** existe um lugar onde as variáveis do sistema são documentadas para os administradores e que precise ser atualizado?