# Spec: Eager load de `lib/` via `config.autoload_lib` e rake desbloqueado em desenvolvimento

## Objetivo

O `lib/` tem dois defeitos de configuração que se cruzam. Esta spec corrige os dois e trava o comportamento correto com testes.

1. **`lib/` nunca é eager loaded.** O `config/application.rb` faz duas coisas:
   - acrescenta `Rails.root.join("lib")`, um `Pathname`, ao `eager_load_paths`;
   - acrescenta `"#{config.root}/lib"`, uma `String`, ao `autoload_paths`.

   O finisher do Rails compara caminhos contra um `Set` de `String`s (`ActiveSupport::Dependencies._eager_load_paths.member?(path)`). Como o `Pathname` nunca casa, o Zeitwerk recebe `do_not_eager_load(lib)`. Consequências:
   - Em `test`, depois de `Rails.application.eager_load!`, continuam com autoload pendente: `Notifier`, `LiquidFormatter`, `ErbFormatter`, `CodeEvaluator` e `Exceptions`.
   - O `zeitwerk:check` não verifica o `lib/`.
   - Em produção, as constantes de `lib/` só carregam na primeira referência, e não no boot.

2. **Qualquer `rake` que dependa de `environment` aborta em desenvolvimento.** Isso acontece desde o active_scaffold 4.3.1 (#621):
   - O `lib/tasks/rcov.rake` faz `require "rspec/core/rake_task"`. Esse require define o módulo `RSpec`, mas não define `RSpec.configure`.
   - O initializer do active_scaffold testa `defined?(RSpec)` e em seguida chama `RSpec.configure`.
   - Isso bloqueia `rake db:setup` (o passo do Quick-install da wiki), `db:migrate`, `zeitwerk:check` e qualquer outra tarefa que carregue o ambiente.

3. **Um bloqueador para corrigir o item 1.** Com o eager load do `lib/` ativo, o boot aborta em `lib/generators/migrate_bigint_generator.rb`. O arquivo tem um `namespace :generate do` solto no topo, o que causa `NoMethodError: undefined method 'namespace' for main`.

**Quem é afetado:** desenvolvedores que montam ou mantêm o ambiente local (Quick-install da wiki) e a suíte de testes, que deve validar o `lib/`.

**Como fica o sucesso:**
- O `lib/` é eager loaded como no template do Rails 7.1+.
- As tarefas rake voltam a funcionar em desenvolvimento.
- Um spec impede regressões.

**Escopo pedido na issue:**
- Substituir as duas linhas de `lib` no `config/application.rb` por `config.autoload_lib(ignore: %w[assets tasks])`.
- Remover `lib/generators/migrate_bigint_generator.rb`.
- Remover `lib/tasks/rcov.rake`.
- Criar `spec/config/autoload_lib_spec.rb` com as premissas listadas em "Critérios de Sucesso".

**Fora de escopo:**
- Alterar o active_scaffold ou a versão dele.
- Mudar a ferramenta de cobertura (simplecov continua).
- Editar a migration `db/migrate/20210830212746_migrate_ids_to_bigint.rb`.

### Premissas

1. A aplicação está em Rails ≥ 7.1, porque `config.autoload_lib` existe a partir dessa versão e a issue cita o guia de upgrade do 7.1. A versão exata não foi informada.
2. O autoloader em uso é o Zeitwerk.
3. As únicas linhas que configuram `lib/` no `config/application.rb` são as duas descritas. Nenhum outro arquivo (por exemplo `config/environments/*`) adiciona `lib/` aos caminhos.
4. `lib/assets` e `lib/tasks` são os únicos subdiretórios de `lib/` que não seguem a convenção do Zeitwerk ou que não devem ser carregados. O restante de `lib/` deve ser eager loaded.
5. O gerador `migrate_bigint_generator.rb` não é referenciado em nenhum lugar, e a migration gerada a partir dele é a fonte de verdade. Basta o histórico do git para preservá-lo.
6. Nenhum outro arquivo de `lib/tasks` ou de `config/` faz `require` parcial do RSpec que reproduza o problema do item 2.
7. Carregar o `lib/` no boot em produção não tem efeito colateral relevante: nenhum código de `lib/` executa lógica no topo do arquivo além de definir constantes.

## Stack Técnica

- Ruby on Rails ≥ 7.1 (versão exata não informada), com Zeitwerk.
- active_scaffold 4.3.2.
- rspec-core 3 e rspec-rails.
- simplecov para cobertura.
- rake.
- Banco de dados e versão do Ruby: não informados na issue original.

## Comandos

Comandos citados na issue:
- Testes com cobertura: `bundle exec rspec`
- Setup do banco (Quick-install da wiki): `rake db:setup`
- Migrações: `rake db:migrate`
- Verificação do Zeitwerk: `rake zeitwerk:check`
- Carregar o ambiente: `rake environment`

Sobre esses comandos:
- A issue não informa se devem ser prefixados com `bundle exec` nem com quais flags.
- Build, lint e servidor de desenvolvimento: não informados na issue original.

## Estrutura do Projeto

Apenas os caminhos citados na issue:

```
config/application.rb                                     → configuração de autoload/eager load de lib/
lib/                                                      → código da aplicação fora de app/ (Notifier, LiquidFormatter, ErbFormatter, CodeEvaluator, Exceptions…)
lib/assets/                                               → ignorado pelo autoload_lib (existência não confirmada)
lib/tasks/                                                → tarefas rake, ignorado pelo autoload_lib
lib/tasks/rcov.rake                                       → a remover
lib/generators/migrate_bigint_generator.rb                → a remover
db/migrate/20210830212746_migrate_ids_to_bigint.rb        → saída do gerador, versionada e mantida
spec/config/autoload_lib_spec.rb                          → novo spec de premissas
```

A estrutura completa do repositório não foi informada na issue original.

## Estilo de Código

Não informado na issue original.

## Estratégia de Testes

- **Framework:** RSpec (rspec-rails). A cobertura vem do simplecov via `bundle exec rspec`.
- **Novo arquivo:** `spec/config/autoload_lib_spec.rb`, com três premissas:
  1. O caminho de `lib/` aparece em `eager_load_paths` como `String`, e não como `Pathname`.
  2. O `lib/` inteiro sobrevive a um eager load forçado (`eager_load(force: true)`) sem levantar erro.
  3. Todo arquivo `.rb` sob `lib/` aparece em `all_expected_cpaths` do loader. Isso garante que o `ignore` não esconde código.
- **Nível:** teste de configuração/integração no ambiente `test`.
- **Verificações manuais em `development`** (não cobertas pela suíte):
  - `rake environment` e `rake zeitwerk:check` sem erro;
  - `rake zeitwerk:check` sem o aviso "lib will only be checked if you configure them to be eager loaded".
- **Meta de cobertura:** não informada na issue original.

## Limites

- **Sempre:**
  - Rodar `bundle exec rspec` completo antes de commitar.
  - Seguir o template do Rails para `autoload_lib`.
  - Manter a migration `20210830212746_migrate_ids_to_bigint.rb` intacta.
- **Perguntar antes:**
  - Ampliar a lista `ignore` além de `assets` e `tasks`.
  - Remover ou mover outros arquivos de `lib/` que eventualmente quebrem o eager load.
  - Alterar a versão do active_scaffold ou contornar o initializer dele.
  - Adicionar `zeitwerk:check` ao CI.
- **Nunca:**
  - Editar código vendorizado ou de gems, como o `engine.rb` do active_scaffold.
  - Reintroduzir o `rcov`.
  - Remover ou pular testes que falhem sem aprovação.
  - Mascarar o problema com um `require "rspec/core"` em desenvolvimento.

## Critérios de Sucesso

1. O `config/application.rb` não contém mais as duas linhas de `lib` e passa a usar `config.autoload_lib(ignore: %w[assets tasks])`.
2. `lib/generators/migrate_bigint_generator.rb` e `lib/tasks/rcov.rake` não existem mais no repositório.
3. Em `test`, depois de `Rails.application.eager_load!`, nenhuma destas constantes tem autoload pendente: `Notifier`, `LiquidFormatter`, `ErbFormatter`, `CodeEvaluator`, `Exceptions`.
4. Em `development`, `rake environment`, `rake db:setup`, `rake db:migrate` e `rake zeitwerk:check` não abortam com `NoMethodError: undefined method 'configure' for module RSpec`.
5. `rake zeitwerk:check` termina sem erros e sem o aviso de que `lib` não é eager loaded.
6. O boot com eager load ativo (produção, ou `eager_load(force: true)`) não levanta `NoMethodError: undefined method 'namespace' for main` nem qualquer outro erro vindo de `lib/`.
7. `spec/config/autoload_lib_spec.rb` existe, cobre as três premissas da Estratégia de Testes e passa.
8. `bundle exec rspec` passa por completo e o simplecov continua gerando cobertura.

## Perguntas em Aberto

1. Qual é a versão exata do Rails, e o `config.load_defaults` já está em 7.1 ou acima?
2. `lib/assets` existe? Há outros subdiretórios de `lib/` (outros geradores em `lib/generators`, templates, arquivos não-Ruby) que também precisem entrar no `ignore` ou ser removidos?
3. Algum arquivo de `lib/` executa código no topo (efeitos colaterais) que passaria a rodar no boot de produção? É aceitável o eventual aumento no tempo de boot?
4. Algum outro arquivo em `lib/tasks` ou em initializers faz `require` parcial do RSpec ou de outra gem de teste em `development`?
5. A wiki (Quick-install) precisa ser atualizada ou receber uma nota sobre o período em que `rake db:setup` estava quebrado?
6. Devemos reportar ao active_scaffold que `defined?(RSpec)` não garante `RSpec.configure`?
7. O `zeitwerk:check` deve passar a rodar no CI para impedir regressões?
8. Algum script, documentação ou processo ainda depende do gerador `migrate_bigint` ou da tarefa `rcov`?