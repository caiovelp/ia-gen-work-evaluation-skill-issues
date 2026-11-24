## Resumo

Dois defeitos de configuração relacionados ao `lib/`, encontrados ao avaliar o `config.autoload_lib` que o guia de upgrade do Rails 7.1 recomenda e que o projeto nunca adotou:

1. **O `lib/` só é autoloaded, nunca eager loaded.** O efeito aparece em todos os ambientes. Em produção, as constantes de `lib/` carregam na primeira referência em vez de no boot.
2. **Qualquer tarefa `rake` que dependa de `environment` aborta em desenvolvimento** desde a atualização para o active_scaffold 4.3.1 (#621). Isso inclui `rake db:setup`, o passo do Quick-install da wiki.

Há também um problema latente. Se o `lib/` passar a ser eager loaded, o boot quebra em `lib/generators/migrate_bigint_generator.rb`.

**Defeito 1 (`lib/` não é eager loaded).** O `config/application.rb` adiciona o `lib/` de duas formas:
- ao `eager_load_paths` como `Pathname` (`Rails.root.join("lib")`);
- ao `autoload_paths` como `String` (`"#{config.root}/lib"`).

O finisher do Rails decide o eager load com `ActiveSupport::Dependencies._eager_load_paths.member?(path)`, que consulta um `Set` de `String`s. O `Pathname` nunca casa, e o Zeitwerk recebe `do_not_eager_load(lib)`.

**Defeito 2 (`rake` aborta em desenvolvimento).**
- `lib/tasks/rcov.rake` faz `require "rspec/core/rake_task"` em development e test.
- Esse require define o módulo `RSpec` sem carregar o `rspec/core` inteiro, então `RSpec.configure` não existe.
- O active_scaffold 4.3 passou a testar `defined?(RSpec)` e a chamar `RSpec.configure` no initializer.
- Em `test` o `rspec-rails` já carregou tudo e o método existe. Em `development` o método não existe.

O `rcov.rake` também está morto por outros motivos:
- a gem `rcov` não está no bundle;
- o `RSpec::Core::RakeTask` do rspec-core 3 não tem `rcov=`, então a tarefa levantaria `NoMethodError` ao rodar;
- a cobertura hoje é feita pelo simplecov via `bundle exec rspec`.

**Problema latente (`migrate_bigint_generator.rb`).** O arquivo `lib/generators/migrate_bigint_generator.rb` tem um `namespace :generate do` solto no topo de um `.rb`, fora de qualquer Rakefile.
- É o gerador descartável da #361 (2021), que produziu `db/migrate/20210830212746_migrate_ids_to_bigint.rb`.
- A saída foi commitada e editada à mão, e nada mais referencia o gerador.
- O bloco `namespace` nunca funcionou, porque o `rake` não carrega `.rb` de `lib/generators`.

## Passos para reproduzir

**A. `lib/` não é eager loaded**
1. No ambiente `test`, inicializar a aplicação e executar `Rails.application.eager_load!`.
2. Verificar se `Notifier`, `LiquidFormatter`, `ErbFormatter`, `CodeEvaluator` e `Exceptions` ainda têm autoload pendente.
3. Opcionalmente, executar `rake zeitwerk:check` e observar o aviso sobre o `lib`.

**B. `rake` aborta em desenvolvimento**
1. Com o active_scaffold 4.3.x no bundle, usar o ambiente `development`.
2. Executar qualquer tarefa que carregue o ambiente, por exemplo `rake db:setup`, `rake db:migrate`, `rake zeitwerk:check` ou `rake environment`.
3. Observar a falha `NoMethodError` em `active_scaffold/engine.rb:77`.
4. Remover `lib/tasks/rcov.rake` e repetir `rake environment`. Desta vez a tarefa passa.

**C. Boot quebra se o `lib/` for eager loaded**
1. Forçar o eager load do `lib/`.
2. Inicializar a aplicação.
3. Observar que o boot aborta ao carregar `lib/generators/migrate_bigint_generator.rb`.

## Comportamento observado

- **A:** depois de `Rails.application.eager_load!` em `test`, `Notifier`, `LiquidFormatter`, `ErbFormatter`, `CodeEvaluator` e `Exceptions` continuam com autoload pendente. O `zeitwerk:check` avisa que o `lib` só será verificado se for configurado para eager load. Em produção, as constantes de `lib/` carregam na primeira referência em vez de no boot.
- **B:** em `development`, toda tarefa `rake` que depende de `environment` aborta com `NoMethodError: undefined method 'configure' for module RSpec`. Produção não é afetada, porque o `rcov.rake` inteiro está atrás de `if Rails.env.development? || Rails.env.test?`.
- **C:** com o eager load do `lib/` forçado, o boot aborta com `NoMethodError: undefined method 'namespace' for main`.

## Comportamento esperado

- O `lib/` deveria ser eager loaded junto com o restante da aplicação. Depois de `eager_load!`, nenhuma constante de `lib/` deveria ficar com autoload pendente, e o `zeitwerk:check` deveria verificar o `lib/`.
- `rake db:setup`, `rake db:migrate`, `rake zeitwerk:check` e as demais tarefas que carregam o ambiente deveriam rodar normalmente em `development`.
- O eager load do `lib/` não deveria quebrar o boot.

## Stack trace / saída de erro

Defeito B, em `development`:

```
NoMethodError: undefined method 'configure' for module RSpec
  active_scaffold-4.3.2/lib/active_scaffold/engine.rb:77
```

Problema C, com eager load do `lib/` forçado:

```
NoMethodError: undefined method 'namespace' for main
```

Aviso do `zeitwerk:check` (trecho citado na issue):

```
lib will only be checked if you configure them to be eager loaded
```

## Caso de teste

A issue não traz código de teste. Os casos mínimos derivados do relato são:

- **A:** no ambiente `test`, após `Rails.application.eager_load!`, nenhuma das constantes `Notifier`, `LiquidFormatter`, `ErbFormatter`, `CodeEvaluator` e `Exceptions` deve estar com autoload pendente. Também é possível verificar se o `lib/` aparece no `eager_load_paths` como `String`. Hoje falha.
- **B:** em `development`, `rake environment` deve terminar sem erro. Hoje falha com o `NoMethodError` acima.
- **C:** forçar o eager load de todo o `lib/` não deve levantar exceção. Hoje falha em `lib/generators/migrate_bigint_generator.rb`.

## Exemplo de código

Trechos citados na issue (não são arquivos completos).

`config/application.rb`, o `lib/` é adicionado com tipos diferentes:

```ruby
# adicionado ao eager_load_paths (Pathname)
Rails.root.join("lib")

# adicionado ao autoload_paths (String)
"#{config.root}/lib"
```

`lib/tasks/rcov.rake`:

```ruby
if Rails.env.development? || Rails.env.test?
  require "rspec/core/rake_task"
  # ...
end
```

`lib/generators/migrate_bigint_generator.rb`, no topo do arquivo:

```ruby
namespace :generate do
  # ...
end
```

## Versão e ambiente

- **active_scaffold:** 4.3.2, conforme o stack trace. O problema começou no lançamento que trouxe o active_scaffold 4.3.1 (#621).
- **rspec-core:** 3.
- **Rails:** a issue cita o guia de upgrade do Rails 7.1. A versão exata em uso não é informada.
- **Autoloader:** Zeitwerk.
- **Cobertura:** simplecov, via `bundle exec rspec`. A gem `rcov` não está no bundle.
- **Ambientes afetados:** o defeito B ocorre em `development`, mas não em `test` (onde o `rspec-rails` carrega o `rspec/core` completo) nem em `production`. O defeito A foi medido em `test`, e o mecanismo é o mesmo em produção.
- **Sistema operacional / versão do Ruby:** Não informado na issue original.