# Especificação: Configuração por fase para exibir notas individuais de outros membros do comitê

## Objetivo

Membros de um comitê de avaliação devem poder ver as notas individuais atribuídas pelos outros membros do mesmo comitê. A visibilidade é controlada por uma nova configuração na **fase**, que permite exibir ou ocultar essas notas.

- **Solicitante:** Raquel, do PPGEET.
- **Usuários afetados:**
  - membros do comitê, que passam a poder ver as notas dos colegas;
  - quem configura a fase, que decide se as notas são exibidas.
- **Por quê:** a justificativa não foi informada na issue. A hipótese mais provável é permitir que o comitê compare avaliações e discuta divergências.

**História de usuário:**
> Como responsável pela configuração de uma fase, quero ativar ou desativar a exibição das notas individuais dos membros do comitê, para que, quando ativada, cada membro possa ver as notas atribuídas pelos demais.

**Critérios de aceitação (esboço):**
- A fase tem uma nova configuração do tipo "exibir notas dos outros membros do comitê" (sim/não).
- Com a configuração desativada, o comportamento atual se mantém: o membro vê apenas as próprias notas.
- Com a configuração ativada, o membro vê as notas individuais de cada outro membro do comitê daquela fase.
- A configuração vale apenas para a fase em que foi definida.

## Premissas

1. O sistema organiza a avaliação em **fases**, e cada fase tem um **comitê** com vários membros que atribuem notas individualmente. Isso foi inferido do texto da issue.
2. Hoje um membro do comitê **não** vê as notas individuais dos outros membros.
3. O valor padrão da nova configuração é **desativado**, para preservar o comportamento atual em fases já existentes e em novas fases.
4. A configuração fica disponível para todos os programas, e não só para o PPGEET. Cada fase decide se a ativa.
5. Só membros do **mesmo comitê, na mesma fase**, veem as notas uns dos outros. Candidatos e usuários externos ao comitê não ganham acesso a nada.
6. As notas exibidas são **somente leitura**. Um membro não edita a nota de outro.
7. A nota aparece identificada pelo membro que a atribuiu, e não de forma anônima.
8. Quem pode alterar a configuração é o mesmo perfil que hoje edita as demais configurações da fase.

→ Sem um humano no processo, estas premissas precisam ser validadas antes da implementação. Veja "Questões em Aberto".

## Stack Tecnológica

Não informado na issue original.

## Comandos

Não informado na issue original.

- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Não informado na issue original. Não se sabe onde ficam:
- o modelo de fase;
- a tela de configuração da fase;
- a tela de avaliação do comitê.

## Estilo de Código

Não informado na issue original. Seguir as convenções já existentes no código das configurações de fase e da tela de avaliação.

## Estratégia de Testes

Framework e localização dos testes não foram informados na issue original. Os níveis de teste esperados, independentemente do framework, são:

- **Unidade / modelo:**
  - a nova configuração existe na fase;
  - o valor padrão é "desativado";
  - o valor é persistido corretamente.
- **Autorização / regra de negócio:**
  - com a configuração desativada, um membro não obtém as notas de outros membros, nem pela interface nem por chamada direta ao backend ou API, se houver;
  - com a configuração ativada, um membro do comitê obtém as notas dos colegas da mesma fase;
  - um usuário que não pertence ao comitê da fase não obtém essas notas em nenhum dos dois casos;
  - a configuração de uma fase não afeta outra fase.
- **Interface / integração:**
  - a opção aparece na tela de configuração da fase;
  - as notas dos outros membros aparecem ou somem conforme a configuração.
- **Regressão:** fases existentes, sem a configuração explicitamente ativada, continuam se comportando como antes.

## Limites

- **Sempre:**
  - manter o padrão "desativado" para não expor notas em fases existentes;
  - verificar a permissão no backend, e não apenas esconder elementos na interface;
  - rodar os testes antes de commitar.
- **Perguntar antes:**
  - alterar o esquema do banco ou criar migrações;
  - mudar quem pode ver ou editar configurações de fase;
  - exibir notas para perfis além dos membros do comitê;
  - adicionar dependências.
- **Nunca:**
  - permitir que um membro edite a nota de outro;
  - expor notas individuais a candidatos ou a usuários externos ao comitê;
  - commitar segredos.

## Critérios de Sucesso

1. As telas de criação e edição de fase têm uma opção para exibir ou ocultar as notas individuais dos outros membros do comitê.
2. Em uma fase nova ou já existente, a opção vem desativada por padrão.
3. Com a opção desativada, nenhum membro do comitê consegue ver as notas individuais dos colegas, nem na interface nem pelo backend.
4. Com a opção ativada, cada membro do comitê vê, para cada candidato ou item avaliado, as notas individuais atribuídas pelos demais membros. A forma de identificar cada membro ainda está pendente: veja a Questão 3.
5. Usuários que não fazem parte do comitê da fase não têm acesso às notas individuais, qualquer que seja o valor da configuração.
6. As notas de outros membros são exibidas apenas para leitura.
7. Os testes cobrem os casos ativado, desativado e usuário fora do comitê, e todos passam.
8. A Raquel (PPGEET) confirma que o comportamento atende à solicitação.

## Questões em Aberto

1. **Momento da exibição:** as notas dos outros devem aparecer sempre, ou só depois que o próprio membro registrar a sua? A segunda opção evita que um membro seja influenciado pelas notas dos colegas.
2. **Quem vê:** todos os membros do comitê, ou apenas o presidente ou coordenador do comitê?
3. **Identificação:** a nota deve aparecer com o nome do avaliador ou de forma anônima ("Avaliador 1", "Avaliador 2")?
4. **Granularidade:** "nota individual" é só a nota final de cada membro, ou também as notas por critério e eventuais comentários ou pareceres?
5. **Mudança durante a fase:** a configuração pode ser alterada depois que a avaliação começou ou depois que já existem notas lançadas? Isso deve ser registrado em log ou auditoria?
6. **Escopo:** a funcionalidade vale para todos os programas, ou só para o PPGEET? Deve existir algum controle por programa além da configuração por fase?
7. **Quem configura:** qual perfil pode alterar essa opção na fase?
8. **Comportamento atual:** hoje os membros já veem alguma nota agregada, como média ou soma? Essa exibição muda com a nova configuração?
9. **Edital e transparência:** há alguma exigência normativa ou de edital sobre o sigilo das notas entre avaliadores que precise ser considerada?
10. **Sistema e código:** qual é a stack, qual é a estrutura do projeto e quais comandos de build e teste são usados? Nada disso consta na issue.