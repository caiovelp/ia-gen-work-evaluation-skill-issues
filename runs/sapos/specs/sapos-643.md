# Spec: Isolamento entre testes: detectar vazamento de `before(:all)` e tornar falhas por ordem reproduzíveis

## Objetivo

**Problema.** Registros criados em `before(:all)` rodam fora da transação por exemplo do `DatabaseCleaner`, que envolve só `around(:each)`. Por isso esses registros são commitados de verdade. Quando o `after(:all)` correspondente não apaga tudo o que foi criado, o registro fica no banco durante parte da suíte. Ele contamina exemplos de outros arquivos e depois some antes do fim da execução.

Caso concreto: a trait `:in_process_with_letters` cria também um `AdmissionProcess` com `simple_url` fixo em `"mestrado"`. O `after(:all)` de `letter_request_spec` não apagava esse registro, e por isso três specs da #636 falhavam na suíte inteira com a mensagem:

```
A validação falhou: URL já está sendo usada no mesmo intervalo por outro processo aberto
```

O detector de vazamento já existente no `after(:suite)` de `spec/rails_helper.rb` não acusou o problema, por dois motivos:
1. Sem eager load fora do CI, varria só 1 classe. Este ponto foi corrigido no PR: 1 → 62 descendants.
2. Ele é **estruturalmente cego** a vazamentos que existem durante a execução mas são limpos antes do `after(:suite)`. Este ponto **não** foi corrigido.

**Já entregue pelo PR (fora do escopo desta spec, registrado como linha de base):**
- `after(:all)` do `letter_request_spec` apaga também o `AdmissionProcess`.
- O detector chama `Rails.application.eager_load!` antes de contar.
- `LEAK_CHECK=strict` transforma o aviso em falha. Não é o padrão.

**Escopo desta spec (o que fica proposto):**
1. **Inventário de dívida via `after(:context)`.** Instrumentar a suíte para detectar, ao fim de cada grupo de exemplos, registros que permaneceram no banco. Isso cobre a classe de vazamento que o `after(:suite)` não enxerga. O objetivo é **medir** quantos dos ~115 arquivos com `before(:all)` vazam, não corrigi-los.
2. **Seed visível no resultado do CI.** Toda execução no CI deve registrar a seed usada, para que falhas dependentes de ordem possam ser reproduzidas com `--seed` e reduzidas com `rspec --bisect`.

**Usuários:** desenvolvedores do projeto que escrevem e depuram specs. Indiretamente, quem decidir sobre a paralelização da suíte.

**Fora do escopo:**
- Corrigir os vazamentos encontrados pelo inventário.
- Tornar `LEAK_CHECK=strict` o padrão.
- Adotar `parallel_tests`. A issue recomenda sanear a dependência de ordem antes de paralelizar.
- Substituir `before(:all)` por outro padrão.

## Premissas

1. O projeto é Rails com RSpec, FactoryBot e DatabaseCleaner, como indicam os trechos da issue.
2. O `DatabaseCleaner` usa estratégia transacional envolvendo apenas `around(:each)`, conforme descrito na issue.
3. O banco de teste começa cada grupo de exemplos em um estado conhecido. Esse estado pode não ser vazio, por exemplo se houver seeds. Por isso a detecção deve comparar a contagem do início com a do fim do grupo (snapshot e diff), e não exigir zero registros. *A confirmar.*
4. Um hook `after(:context)` registrado em `config` roda **depois** dos `after(:all)` definidos no próprio grupo. Assim, ele vê o estado após a limpeza manual. *A verificar na versão do RSpec em uso.*
5. Hooks `before/after(:context)` registrados em `config` se aplicam a grupos de nível superior. Vazamentos em grupos aninhados seriam então observados ao fim do grupo raiz do arquivo. *A verificar.* Ver Questões em Aberto.
6. O inventário reaproveita a mesma enumeração de modelos do detector atual (`Rails.application.eager_load!` + `ApplicationRecord.descendants`), para não criar uma segunda fonte de verdade.
7. O inventário é **informativo por padrão**: reporta e não falha a suíte. Isso segue a mesma lógica de não tornar `LEAK_CHECK=strict` o padrão.
8. O "CI" mencionado é o ambiente onde `ENV["CI"]` está presente (`config/environments/test.rb:22`).

## Stack Tecnológica

- Ruby on Rails. Versão não informada na issue original.
- RSpec. Versão não informada na issue original.
- FactoryBot.
- DatabaseCleaner, com estratégia transacional por exemplo.
- `parallel_tests` é mencionado apenas como possibilidade futura e não está em uso.
- Banco de dados: não informado na issue original.
- Provedor de CI: não informado na issue original.

## Comandos

Conhecidos pela issue:

```
# Reprodução mínima do caso (antes da correção)
rspec './spec/models/admissions/letter_request_spec.rb[1:4:2]' \
      './spec/requests/goldens/reports_golden_spec.rb[1:9:1,1:9:2,1:9:3]' --seed 17813

# Redução de falha dependente de ordem
rspec --bisect --seed <SEED>

# Detector de vazamento em modo estrito (falha em vez de avisar)
LEAK_CHECK=strict rspec
```

Desconhecidos:
- Comando exato da suíte no CI: não informado na issue original.
- Variável ou flag para ativar o inventário por `after(:context)`: a definir. Ver Questões em Aberto.
- Lint: não informado na issue original.

## Estrutura do Projeto

Caminhos citados na issue:

```
spec/rails_helper.rb                              → configuração do RSpec; contém o detector after(:suite) e LEAK_CHECK
config/environments/test.rb                       → linha 22: config.eager_load = ENV["CI"].present?
spec/models/admissions/letter_request_spec.rb     → caso que vazava AdmissionProcess via before(:all)
spec/requests/goldens/reports_golden_spec.rb      → spec afetado pelo vazamento
```

- Onde ficam as factories (trait `:in_process_with_letters`): não informado na issue original.
- Arquivo de configuração do CI: não informado na issue original.
- Se o inventário deve ficar em `spec/rails_helper.rb` ou em `spec/support/`: não informado na issue original.

## Estilo de Código

Não informado na issue original.

O único padrão observável é o de setup e limpeza manual que originou o problema:

```ruby
before(:all) do
  @admission_application = FactoryBot.create(:admission_application, :in_process_with_letters)
end
after(:all) do
  @admission_application.delete
  @filled_form.delete
end
```

A nova instrumentação deve seguir as convenções já usadas em `spec/rails_helper.rb`, que não são visíveis aqui.

## Estratégia de Testes

- **Validação do inventário contra o caso conhecido.** Reintroduzir temporariamente o vazamento em `letter_request_spec`, removendo a exclusão do `AdmissionProcess` no `after(:all)`. O inventário deve reportar esse arquivo ou grupo e o modelo `AdmissionProcess`. Com a correção do PR presente, o arquivo não deve aparecer.
- **Prova de que o `after(:suite)` não basta.** No mesmo cenário reintroduzido, confirmar que o detector `after(:suite)` continua sem acusar e que o `after(:context)` acusa. Isso demonstra que a lacuna estrutural foi coberta.
- **Regressão da suíte.** Rodar a suíte completa com as seeds já usadas no PR (17813, 4242, 90210, 31337). O resultado não pode ter novas falhas: linha de base de 2263 exemplos e 0 falhas. O inventário apenas reporta.
- **Custo.** Medir o tempo da suíte com e sem a instrumentação. O snapshot por grupo implica contagens em ~62 modelos a cada grupo de nível superior.
- **Seed no CI.** Verificar no log de uma execução real do CI que a seed aparece e que, usada localmente com `--seed`, reproduz a mesma ordem.
- Framework de cobertura e metas de cobertura: não informado na issue original.

## Limites

- **Sempre:**
  - Manter o inventário não-bloqueante por padrão.
  - Reportar, por vazamento, o arquivo ou grupo de origem, o modelo e a quantidade de registros.
  - Usar `eager_load!` antes de enumerar modelos.
  - Rodar a suíte com múltiplas seeds antes de concluir.
- **Perguntar antes:**
  - Tornar o inventário ou o `LEAK_CHECK=strict` bloqueante.
  - Corrigir em massa os `after(:all)` dos ~115 arquivos.
  - Alterar a estratégia do `DatabaseCleaner`.
  - Mudar `config.eager_load` em `config/environments/test.rb`.
  - Adicionar gems.
  - Alterar a configuração do CI além de expor a seed.
  - Iniciar qualquer trabalho de paralelização.
- **Nunca:**
  - Apagar dados automaticamente no hook de inventário. Isso mascararia a dívida que se quer medir.
  - Remover ou pular specs que passem a acusar vazamento.
  - Fixar uma seed no CI no lugar da ordem aleatória.

## Critérios de Sucesso

1. Existe instrumentação em `after(:context)` que, ao fim de cada grupo, compara as contagens por modelo com o estado do início do grupo e reporta as diferenças.
2. Com o vazamento do `letter_request_spec` reintroduzido, o relatório aponta `AdmissionProcess` e o arquivo de origem. Com a correção, não aponta.
3. O relatório da suíte completa produz um inventário consolidado: lista de arquivos ou grupos com vazamento, modelos e quantidades. Esse inventário responde à pergunta "quantos dos ~115 arquivos com `before(:all)` esquecem algum registro?".
4. Sem ativar modo estrito, a suíte completa continua com 0 falhas nas seeds 17813, 4242, 90210 e 31337.
5. O comportamento atual do detector `after(:suite)` e do `LEAK_CHECK=strict` permanece inalterado.
6. Toda execução da suíte no CI exibe a seed em local consultável no resultado, sem precisar baixar artefatos.
7. O acréscimo de tempo da suíte causado pela instrumentação é medido e documentado. O limite aceitável ainda não foi definido; ver Questões em Aberto.

## Questões em Aberto

1. **Divisão do escopo.** O inventário por `after(:context)` e o registro da seed no CI são independentes e podem ser entregues e verificados separadamente. Devem ser specs e PRs distintos?
2. **Ativação do inventário.** Deve rodar sempre, só no CI, ou só sob uma variável (por exemplo, uma extensão de `LEAK_CHECK`)? Qual nome?
3. **Grupos aninhados.** `before(:all)` em grupo aninhado, como o exemplo `[1:4:2]`, pode vazar e ser limpo por um `after(:all)` do grupo externo antes do fim do arquivo. Isso precisa ser detectado? Se sim, o hook deve ser aplicado a todos os grupos e não só aos de nível superior, com o custo correspondente.
4. **Estado inicial do banco.** O banco de teste está vazio no início da suíte e de cada grupo, ou há seeds e dados de referência? Isso define se basta checar zero ou se é necessário fazer diff.
5. **Formato e destino do inventário.** Saída no console, arquivo (JSON ou CSV) como artefato do CI, ou ambos?
6. **Orçamento de desempenho.** Qual é o aumento de tempo aceitável da suíte com a instrumentação ativa?
7. **Exposição da seed no CI.** O RSpec já imprime a seed na saída com `--order random`? A seed precisa aparecer em um local mais visível, como resumo do job ou nome de artefato? Qual é o provedor de CI?
8. **Próximo passo após o inventário.** Medida a dívida, qual é o critério para decidir entre corrigir os `after(:all)` um a um, migrar para outro padrão de setup ou tornar o modo estrito o padrão?
9. **Contorno na #636.** O contorno adicionado no spec da #636 deve ser removido agora que a reprodução mínima passa sem ele?
10. **`delete` vs `destroy`.** O `after(:all)` usa `delete`, que não dispara callbacks nem `dependent:`. Faz parte da investigação verificar se isso contribui para outros vazamentos?