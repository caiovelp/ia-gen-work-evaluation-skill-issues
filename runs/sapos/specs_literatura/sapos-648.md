## Resumo

O subform de **Bolsas** na tela de Matrícula (`/enrollments/:id/edit`) não exibe mais o campo do código da bolsa (`:scholarship`). Os campos restantes são Data de Início, Data Limite de Concessão, Data de Encerramento e Observação. Sem o campo, não é possível cadastrar uma bolsa para um aluno por essa tela.

É uma regressão. O campo deixou de aparecer a partir do commit `4f5270ea` (08/06/2026, *"Update active scaffold to 4.0.13"*), que faz parte do salto de versão descrito em #621.

Análise do autor:
- O commit passou a declarar `config.subform.columns` no `ScholarshipDurationsController`, e essa lista não inclui `:scholarship`.
- No active_scaffold, `subform.columns` é declarado como `columns_accessor :columns, copy: :update`. Sem declaração explícita, ele herda as colunas de update, que no controller começam por `:scholarship`.
- Essa linha é idêntica no ref fixado antes (`6210cdc`, versão 3.6.99) e na 4.0.13. A herança não mudou. O que mudou foi a declaração explícita da lista, que substitui a herança inteira.
- A intenção do commit parece ter sido remover `:scholarship_suspensions`, que é subform e não se renderiza dentro de outro subform. O `:scholarship` foi removido junto.

O problema não se limita à exibição:
1. **O salvamento também ignora a coluna.** O `attribute_params` do active_scaffold usa `subform.columns` como lista de atributos aceitos do registro aninhado. O trecho é `record_columns = active_scaffold_config_for(record.class).subform.columns`, repassado a `update_record_from_params`. Por isso a bolsa seria descartada mesmo num POST montado à mão.
2. **A Data Limite de Concessão é calculada de forma incompleta.** `ScholarshipDuration#update_end_date` usa o mínimo entre a data derivada do nível da matrícula e a `end_date` da bolsa. Sem bolsa selecionada, só a primeira entra no cálculo. O recálculo ao escolher a bolsa (`config.columns[:scholarship].update_columns = [:end_date]` com `send_form_on_update_column`) também nunca dispara, porque não existe o campo que o acionaria.

Alcance:
- A tela de **Bolsas** (`/scholarships`) tem o mesmo subform de `ScholarshipDuration` e **não foi afetada**. Ali o pai é a bolsa, que o active_scaffold esconde, e o campo Matrícula continua na lista. Pelo lado da bolsa ainda era possível vincular a matrícula; pelo lado da matrícula, não. Segundo o autor, isso ajuda a explicar por que o defeito passou dois meses sem ser notado.
- O mesmo commit também alterou a lista de colunas do `PhaseDurationsController`. Nada se perdeu ali: `PhaseDuration` só tem essas quatro colunas mais `:phase`, que é o pai no subform de Fases e fica escondido de qualquer forma.

## Passos para reproduzir

1. Use uma versão que inclua o commit `4f5270ea` (active_scaffold 4.0.13).
2. Abra a tela de edição de uma matrícula: `/enrollments/:id/edit`.
3. Localize o subform de **Bolsas**, ou seja, a tabela cujo `id` termina em `scholarship_durations-subform-list`.
4. Observe os campos disponíveis para uma nova bolsa.
5. (Opcional) Envie um POST montado à mão com `record[scholarship_durations][...][scholarship]` preenchido. O valor da bolsa é descartado.

## Comportamento observado

Os `<label>` extraídos do HTML de `/enrollments/:id/edit`, na tabela `table[id$='scholarship_durations-subform-list']`, são:

```
Data de Início
Data Limite de Concessão
Data de Encerramento
Observação
```

- Não há campo para selecionar a bolsa, então não é possível cadastrar bolsa para o aluno por essa tela.
- Um parâmetro `scholarship` enviado no subform é ignorado no salvamento.
- A Data Limite de Concessão considera apenas a data derivada do nível da matrícula.

O autor escreveu uma varredura que percorre todos os controllers do active_scaffold. Ela procura associações renderizadas como subform cujas colunas obrigatórias do filho (`belongs_to` sem `optional`, ou validação de presença) ficaram fora do `subform.columns`, descontando a associação com o pai. No estado atual, a varredura acusa exatamente um caso:

```
EnrollmentsController > scholarship_durations (ScholarshipDuration)
  subform:             [:enrollment, :start_date, :end_date, :cancel_date, :obs]
  pai (oculto):        :enrollment
  obrigatória ausente: [:scholarship]
```

Uma segunda passada, mais frouxa, compara cada subform com o formulário próprio do filho. O único desvio que ela aponta é `:scholarship_suspensions`, que está fora de propósito.

## Comportamento esperado

O subform de Bolsas na tela de Matrícula deve exibir o campo do código da bolsa, como antes do commit `4f5270ea`:

```
Número da Bolsa
Data de Início
Data Limite de Concessão
Data de Encerramento
Observação
```

O campo deve ser o widget de record_select, apontando para o browse de bolsas:

```html
<input type="text" name="record[scholarship_durations][...][scholarship]"
       class="scholarship-input update_form text-input recordselect"
       data-rs-url="/scholarships/browse" ... />
```

Além disso:
- A bolsa selecionada deve ser aceita e salva.
- A Data Limite de Concessão deve considerar também a `end_date` da bolsa.
- O campo deve ser recalculado ao escolher a bolsa.

## Stack trace / saída de erro

Não informado na issue original. O defeito não gera erro; os dados de diagnóstico estão em "Comportamento observado".

## Caso de teste

Caso de teste mínimo, derivado do que a issue descreve (teste de feature em `spec/features/enrollments_spec.rb`):

1. Acesse a página de edição de uma matrícula (`/enrollments/:id/edit`).
2. No subform de Bolsas (`table[id$='scholarship_durations-subform-list']`), verifique que existe o label "Número da Bolsa".
3. Verifique que existe o input `record[scholarship_durations][...][scholarship]` com a classe `recordselect` e `data-rs-url="/scholarships/browse"`.

Segundo o autor, esse teste falha no estado atual.

Cobertura atual:
- Nenhum exemplo da suíte passa pelo subform de Bolsas da tela de Matrícula.
- `spec/features/enrollments_spec.rb` só toca em bolsa pela busca (`scholarship_durations_active`).
- `spec/features/scholarship_durations_spec.rb` exercita a tela própria de `ScholarshipDuration`, onde o campo nunca esteve em risco.

## Exemplo de código

Trecho adicionado ao `ScholarshipDurationsController` pelo commit `4f5270ea`:

```ruby
config.subform.columns = [
  :enrollment, :start_date, :end_date, :cancel_date, :obs
]
```

Declaração no active_scaffold, idêntica em `6210cdc` (3.6.99) e na 4.0.13:

```ruby
columns_accessor :columns, copy: :update
```

Trecho de `attribute_params` que usa `subform.columns` como lista de atributos aceitos:

```ruby
record_columns = active_scaffold_config_for(record.class).subform.columns
```

Encadeamento de recálculo da Data Limite de Concessão, que depende do campo `:scholarship`:

```ruby
config.columns[:scholarship].update_columns = [:end_date]
```

Usado em conjunto com `send_form_on_update_column`.

Lista de colunas do `PhaseDurationsController` alterada no mesmo commit (sem perda de campo):

```ruby
config.columns = [:deadline_semesters, :deadline_months, :deadline_days, :level]
```

## Versão e ambiente

- Commit que introduziu a regressão: `4f5270ea` (08/06/2026, *"Update active scaffold to 4.0.13"*), parte do salto de versão descrito em #621.
- active_scaffold: 4.0.13 (afetado). Ref fixado anteriormente: `6210cdc` (3.6.99, não afetado).
- Versões de Ruby, Rails, navegador e sistema operacional: não informadas na issue original.