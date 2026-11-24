# Spec: Tratamento da exclusão de Aluno e Professor vinculados a Usuário

## Objetivo

Hoje é possível excluir um Aluno ou Professor que está vinculado a um Usuário, e nada acontece com esse Usuário. Ele continua com o role "Aluno" ou "Professor", mas sem uma instância real correspondente. Isso viola a regra de negócio abaixo.

> Todo usuário que possui o role Professor ou Aluno tem que estar obrigatoriamente ligado a uma instância real dos respectivos.

O objetivo é tratar a exclusão de Aluno e Professor vinculados a Usuário para que essa regra nunca seja violada.

**Usuários afetados:** quem administra o cadastro de alunos, professores e usuários, e os próprios usuários vinculados, cujo acesso depende do role.

**Soluções propostas na issue, ainda sem escolha definida:**

1. **Bloquear:** impedir a exclusão de Alunos e Professores ligados a usuários.
2. **Rebaixar o role:** ao excluir, remover do usuário o role correspondente (Aluno ou Professor). Se for o único role do usuário, ele passa a ter somente o role "Desconhecido".

**Critérios de aceitação gerais, válidos para qualquer opção:**
- Após qualquer operação de exclusão, nenhum usuário com role Aluno fica sem Aluno vinculado.
- Após qualquer operação de exclusão, nenhum usuário com role Professor fica sem Professor vinculado.
- A exclusão de Aluno ou Professor **sem** usuário vinculado continua funcionando como hoje.

**Comportamento esperado na Opção 1 (bloquear):**
- A exclusão de Aluno ou Professor vinculado a usuário é rejeitada.
- O usuário recebe uma mensagem de erro que explica o motivo.
- Nenhum dado é alterado: Aluno, Professor e Usuário continuam intactos.

**Comportamento esperado na Opção 2 (rebaixar role):**
- Ao excluir um Aluno vinculado, o role "Aluno" é removido do usuário.
- Ao excluir um Professor vinculado, o role "Professor" é removido do usuário.
- Se o usuário ficar sem nenhum role, ele recebe o role "Desconhecido".
- Se o usuário tiver outros roles, eles são mantidos e "Desconhecido" **não** é adicionado.
- A exclusão e o ajuste de roles acontecem de forma atômica: ou ambos são aplicados, ou nenhum.

## Premissas

1. O sistema tem as entidades Usuário, Aluno e Professor, e um Usuário se associa a no máximo um Aluno e/ou um Professor.
2. Um Usuário pode ter múltiplos roles, já que a issue fala em "caso seja o único role".
3. O role "Desconhecido" já existe no sistema.
4. A exclusão citada é a exclusão definitiva (hard delete), feita pela interface ou API de cadastro de Alunos e Professores.
5. A imagem anexada à issue mostra um usuário com role Aluno ou Professor sem instância vinculada após a exclusão. O conteúdo da imagem não pôde ser verificado.
6. O tratamento deve ser igual para Aluno e Professor.

## Stack Tecnológica

Não informado na issue original.

## Comandos

Não informado na issue original. Os comandos de build, teste, lint e dev são desconhecidos.

## Estrutura do Projeto

Não informado na issue original. Os locais das entidades Usuário, Aluno e Professor, dos serviços de exclusão e dos testes são desconhecidos.

## Estilo de Código

Não informado na issue original. Seguir as convenções já existentes no repositório.

## Estratégia de Testes

O framework de testes e o local dos testes não são informados na issue original. Cenários mínimos a cobrir, conforme a opção escolhida:

- Excluir Aluno sem usuário vinculado: sucesso.
- Excluir Professor sem usuário vinculado: sucesso.
- Excluir Aluno vinculado a usuário:
  - Opção 1: a exclusão é bloqueada e os dados ficam inalterados.
  - Opção 2: o role "Aluno" é removido do usuário.
- Excluir Professor vinculado a usuário: casos equivalentes aos do Aluno.
- Opção 2, usuário cujo único role era Aluno ou Professor: ele fica apenas com "Desconhecido".
- Opção 2, usuário com outros roles, por exemplo Professor e Admin: o role removido some, os demais permanecem e "Desconhecido" não é adicionado.
- Opção 2, falha durante o ajuste de roles: a exclusão é revertida.
- Teste de integração ou regressão que reproduza o cenário da imagem da issue.

## Limites

- **Sempre:**
  - Manter a regra de que role Aluno ou Professor implica uma instância vinculada.
  - Cobrir com testes os casos com e sem vínculo.
  - Tratar Aluno e Professor de forma simétrica.
- **Perguntar antes:**
  - Alterar o schema do banco, por exemplo constraints de FK ou `ON DELETE`.
  - Escolher entre a Opção 1 e a Opção 2.
  - Corrigir dados já inconsistentes em produção.
  - Mudar o contrato da API de exclusão, como códigos de status e formato de erro.
- **Nunca:**
  - Excluir o Usuário em cascata ao excluir Aluno ou Professor, pois isso não está previsto na issue.
  - Deixar um usuário sem nenhum role.
  - Remover roles não relacionados à entidade excluída.

## Critérios de Sucesso

- [ ] A opção de tratamento (1 ou 2) foi definida e implementada.
- [ ] Não é mais possível chegar ao estado mostrado na issue, ou seja, um usuário com role Aluno ou Professor sem instância vinculada, pela exclusão de Aluno ou Professor.
- [ ] A exclusão de Aluno ou Professor sem vínculo se comporta como antes.
- [ ] Se for adotada a Opção 1: a tentativa de exclusão retorna um erro claro e não altera dados.
- [ ] Se for adotada a Opção 2:
  - o role correto é removido;
  - usuários sem roles restantes recebem "Desconhecido";
  - os demais roles são preservados;
  - a operação é atômica.
- [ ] Os testes automatizados cobrindo os cenários da Estratégia de Testes passam.

## Questões em Aberto

1. **Qual opção adotar: 1 (bloquear) ou 2 (rebaixar role)?** Pode ser uma combinação, por exemplo bloquear por padrão e permitir a exclusão com confirmação explícita.
2. Na Opção 1, qual mensagem deve ser exibida? Ela deve indicar qual usuário está vinculado ou oferecer um atalho para desvincular?
3. Na Opção 2, o usuário afetado ou o administrador deve ser notificado da mudança de role? Sessões ativas do usuário devem ser invalidadas ou atualizadas?
4. Já existem usuários em estado inconsistente na base? Deve haver migração ou script de correção para eles?
5. Existem outros caminhos que quebram a mesma regra e devem entrar no escopo? Exemplos: desvincular um usuário de um Aluno ou Professor sem excluí-lo, ou atribuir manualmente o role Aluno ou Professor a um usuário sem instância.
6. Há exclusões em massa ou exclusão lógica (soft delete) de Aluno ou Professor que precisem do mesmo tratamento?
7. Qual é a stack, quais são os comandos de build e teste, e onde ficam os serviços de exclusão e os testes no repositório?