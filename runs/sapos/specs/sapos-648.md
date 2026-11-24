# Especificação: Restaurar o campo de bolsa no subform de Bolsas da tela de Matrícula

## Objetivo

Restaurar a possibilidade de cadastrar uma bolsa para um aluno pela tela de Matrícula (`/enrollments/:id/edit`), no subform de **Bolsas** (`scholarship_durations`).

**Contexto da regressão:**
- O commit `4f5270ea` (08/06/2026, *"Update active scaffold to 4.0.13"*, ligado à #621) declarou `config.subform.columns` no `ScholarshipDurationsController`.
- Antes, o subform herdava as colunas de update (`columns_accessor :columns, copy: :update`), que começam por `:scholarship`. Esse comportamento é idêntico na 3.6.99 (`6210cdc`) e na 4.0.13.
- A lista declarada substituiu a herança inteira e deixou `:scholarship` de fora.
- A intenção provável era excluir apenas `:scholarship_suspensions`, um subform aninhado que não se renderiza dentro de outro subform.

**Usuário:** quem opera a tela de Matrícula e precisa vincular bolsas a alunos.

**Impactos atuais:**
1. **Campo ausente.** O campo "Número da Bolsa" não aparece no subform, e não há o que selecionar.
2. **Salvamento descarta o atributo.** O `attribute_params` do active_scaffold usa `subform.columns` como lista de atributos aceitos. Por isso, `scholarship` é descartado mesmo num POST montado à mão. Reexibir o campo por CSS ou JS não resolve.
3. **Data Limite de Concessão calculada só pela metade.**
   - `ScholarshipDuration#update_end_date` deixa de considerar a `end_date` da bolsa.
   - O recálculo encadeado (`config.columns[:scholarship].update_columns = [:end_date]` com `send_form_on_update_column`) nunca dispara.

**Fora do escopo:**
- A tela de Bolsas (`/scholarships`) não foi afetada.
- O `PhaseDurationsController` foi alterado no mesmo commit, mas nada se perdeu ali.

**Critérios de aceitação (histórias):**
- Como operador, ao editar uma matrícula, vejo o campo "Número da Bolsa" no subform de Bolsas, como widget record_select apontando para `/scholarships/browse`.
- Ao selecionar a bolsa e salvar, a `ScholarshipDuration` é persistida com a bolsa vinculada.
- Ao selecionar a bolsa, a Data Limite de Concessão é recalculada considerando a `end_date` da bolsa.

## Premissas

1. A correção restringe-se a recolocar `:scholarship` em `config.subform.columns` do `ScholarshipDurationsController`. `:scholarship_suspensions` continua fora de propósito.
2. A ordem da lista define a ordem na tela, e `:scholarship` deve vir primeiro, como era antes da regressão. A lista esperada de labels é: Número da Bolsa, Data de Início, Data Limite de Concessão, Data de Encerramento, Observação.
3. `:enrollment` continua na lista e continua oculto no subform da Matrícula, por ser o pai. Na tela de Bolsas, ele segue visível.
4. A versão do active_scaffold permanece 4.0.13. Não há downgrade nem patch na gem.
5. `scholarship` é obrigatória em `ScholarshipDuration` (`belongs_to` sem `optional` ou validação de presença), conforme a varredura relatada. Por isso, cadastros feitos pela tela de Matrícula nesses dois meses devem ter falhado na validação, em vez de gravar registros sem bolsa.
6. A varredura de subforms descrita na issue é ferramenta de diagnóstico do autor e não está no repositório.

## Stack Tecnológica

- Ruby on Rails, versões **não informadas na issue original**.
- active_scaffold 4.0.13, antes fixado em `6210cdc` (3.6.99).
- record_select, usado no widget de seleção de bolsa.
- Testes de feature em `spec/features/`, sugerindo RSpec com testes de navegador. A ferramenta de navegação (Capybara ou outra) é **desconhecida**.

## Comandos

- Build: desconhecido.
- Testes: desconhecido. A issue não informa o comando para rodar `spec/features/enrollments_spec.rb`.
- Lint: desconhecido.
- Dev: desconhecido.

## Estrutura do Projeto

- `spec/features/enrollments_spec.rb`: testes de feature da tela de Matrícula. Hoje só toca em bolsa pela busca (`scholarship_durations_active`).
- `spec/features/scholarship_durations_spec.rb`: testes da tela própria de `ScholarshipDuration`.
- `ScholarshipDurationsController`, `EnrollmentsController`, `PhaseDurationsController` e o model `ScholarshipDuration`: os caminhos dos arquivos são **desconhecidos** (não informados na issue).

## Estilo de Código

Não informado na issue original. O único trecho de referência é a declaração de colunas do active_scaffold citada na issue:

```ruby
config.subform.columns = [
  :enrollment, :start_date, :end_date, :cancel_date, :obs
]
```

## Estratégia de Testes

- **Teste de feature, novo:** um exemplo em `spec/features/enrollments_spec.rb`, na página de edição da matrícula. Ele confere:
  - a presença da coluna "Número da Bolsa" no `table[id$='scholarship_durations-subform-list']`;
  - o widget record_select: `input` com classe `recordselect`, `name` contendo `[scholarship_durations][...][scholarship]` e `data-rs-url="/scholarships/browse"`.
- O exemplo deve **falhar sem a correção e passar com ela**. O autor relata ter verificado os dois lados.
- **Cobertura desejável, a confirmar (ver Perguntas em Aberto):**
  - teste de persistência, em que o envio do subform com bolsa grava o vínculo;
  - teste do recálculo da Data Limite de Concessão ao selecionar a bolsa;
  - teste de regressão genérico baseado na varredura (colunas obrigatórias fora de `subform.columns`).
- **Não regressão:**
  - `spec/features/scholarship_durations_spec.rb` e o subform de Bolsas em `/scholarships` continuam funcionando;
  - a varredura não acusa nenhum caso.

## Limites

- **Sempre:**
  - manter `:scholarship_suspensions` fora do `subform.columns`;
  - rodar a suíte de features de matrícula e de bolsas antes de concluir;
  - preservar a ordem das colunas conforme a lista esperada.
- **Perguntar antes:**
  - alterar a versão do active_scaffold ou aplicar monkey patch;
  - adicionar a varredura de subforms à suíte ou à CI;
  - qualquer correção de dados já gravados;
  - mexer no `PhaseDurationsController`.
- **Nunca:**
  - contornar a falta do campo por CSS ou JS, já que o salvamento descarta o atributo;
  - remover `subform.columns` e voltar à herança sem avaliar o efeito sobre `:scholarship_suspensions`;
  - alterar o comportamento da tela de Bolsas (`/scholarships`).

## Critérios de Sucesso

1. Em `/enrollments/:id/edit`, os `<label>` do `table[id$='scholarship_durations-subform-list']` são, nesta ordem: **Número da Bolsa, Data de Início, Data Limite de Concessão, Data de Encerramento, Observação**.
2. O campo de bolsa é renderizado como `input.recordselect` com `name="record[scholarship_durations][...][scholarship]"` e `data-rs-url="/scholarships/browse"`.
3. Ao salvar a matrícula com uma bolsa selecionada no subform, a `ScholarshipDuration` criada fica vinculada à bolsa escolhida.
4. Ao selecionar uma bolsa, a Data Limite de Concessão é recalculada como o mínimo entre a data derivada do nível da matrícula e a `end_date` da bolsa.
5. O subform de Bolsas não renderiza `:scholarship_suspensions`.
6. A tela `/scholarships` e seu subform de `ScholarshipDuration` continuam inalterados.
7. O novo exemplo em `spec/features/enrollments_spec.rb` falha sem a correção e passa com ela, e a suíte existente continua verde.
8. A varredura de subforms não acusa nenhuma coluna obrigatória ausente.

## Perguntas em Aberto

1. Os critérios 3 e 4 (persistência e recálculo da Data Limite de Concessão) devem ganhar testes automatizados próprios, ou basta o exemplo de renderização proposto na issue?
2. A varredura de subforms deve virar teste permanente para evitar regressões semelhantes em outros controllers?
3. Algum registro de `ScholarshipDuration` foi criado ou editado pela tela de Matrícula entre 08/06/2026 e a correção, com `end_date` calculada sem a bolsa? É necessário auditar ou corrigir dados?
4. A posição de `:scholarship` como primeira coluna é a desejada, reproduzindo a ordem anterior das colunas de update?
5. Quais são o comando de testes, as versões de Ruby/Rails e os caminhos dos arquivos dos controllers e do model envolvidos?
6. A #621 precisa ser atualizada ou referenciada na correção?