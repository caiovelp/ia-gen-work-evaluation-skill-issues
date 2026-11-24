# Isolamento entre testes: `before(:all)` escapa da transação e o detector de vazamento não acusa

## Resumo

Registros criados em `before(:all)` ficam fora da transação por exemplo do `DatabaseCleaner`, que envolve apenas `around(:each)`. Por isso esses registros são commitados de verdade. No `letter_request_spec`, a trait `:in_process_with_letters` cria um `AdmissionProcess` com `simple_url` fixo em `"mestrado"`. O `after(:all)` apaga só dois dos três registros criados. O `AdmissionProcess` que sobra faz falhar specs que rodam depois dele, por violação de validação de unicidade. As falhas dependem da ordem de execução.

O detector de vazamento do `after(:suite)` em `spec/rails_helper.rb` não acusou o problema, por dois motivos independentes:

1. Fora do CI, ele varre uma lista quase vazia de modelos, porque o eager load só é ativado no CI.
2. Ele não consegue detectar vazamentos que existem durante a execução e são limpos antes do fim da suíte.

## Passos para reproduzir

**Falha dependente de ordem:**

1. Executar a reprodução mínima obtida com `rspec --bisect`. O bisect reduziu 2253 exemplos a um:
   ```
   rspec './spec/models/admissions/letter_request_spec.rb[1:4:2]' \
         './spec/requests/goldens/reports_golden_spec.rb[1:9:1,1:9:2,1:9:3]' --seed 17813
   ```
2. Observar que os exemplos de `reports_golden_spec.rb` falham com erro de validação de URL.
3. Rodar os mesmos specs isoladamente e observar que passam.

**Detector inerte fora do CI:**

1. Rodar a suíte localmente, sem a variável `CI` definida.
2. Verificar `ApplicationRecord.descendants`: retorna **1** elemento.

**Detector cego a vazamentos de `before(:all)`:**

1. Rodar `spec/models/admissions/letter_request_spec.rb` isoladamente.
2. Consultar o banco ao final: ele está limpo.
3. Durante a execução, porém, o registro de `AdmissionProcess` existe, como mostra a sonda descrita em "Comportamento observado".

## Comportamento observado

- Três specs novos, escritos como testes de caracterização da #636, passam isolados e falham na suíte inteira, todos com a mesma mensagem de validação.
- Uma sonda no momento da falha confirma que um `AdmissionProcess` vazado está presente:
  ```
  1 processo(s): [[1, "mestrado", 01/01/2024, 01/02/2024]]
  ```
- O `after(:all)` do `letter_request_spec` apaga `@admission_application` e `@filled_form`, mas não o `AdmissionProcess` criado pela trait.
- Sem eager load, que é o caso fora do CI, `ApplicationRecord.descendants` devolve 1 elemento. O detector só funciona de fato no CI, onde quem desenvolve não vê o aviso.
- Mesmo com a lista completa de modelos, o detector no `after(:suite)` conta os registros depois que o vazamento já sumiu. Ele só pega vazamentos que persistem até o fim da suíte.

## Comportamento esperado

- Os specs passam independentemente da ordem de execução e da seed, ou seja, há isolamento entre testes.
- Registros criados em `before(:all)` são totalmente removidos ao final do contexto.
- O detector de vazamento acusa registros vazados também fora do CI, inclusive vazamentos que existem só durante parte da execução.

## Stack trace / saída de erro

Mensagem de erro dos specs que falham:

```
A validação falhou: URL já está sendo usada no mesmo intervalo por outro processo aberto
```

Saída da sonda no momento da falha:

```
1 processo(s): [[1, "mestrado", 01/01/2024, 01/02/2024]]
```

Nenhum stack trace foi informado na issue original.

## Caso de teste

Reprodução mínima obtida via `rspec --bisect`:

```
rspec './spec/models/admissions/letter_request_spec.rb[1:4:2]' \
      './spec/requests/goldens/reports_golden_spec.rb[1:9:1,1:9:2,1:9:3]' --seed 17813
```

## Exemplo de código

Trecho de `spec/models/admissions/letter_request_spec.rb` que causa o vazamento:

```ruby
before(:all) do
  @admission_application = FactoryBot.create(:admission_application, :in_process_with_letters)
end
after(:all) do
  @admission_application.delete
  @filled_form.delete
end
```

Configuração que deixa o detector inerte fora do CI (`config/environments/test.rb:22`):

```ruby
config.eager_load = ENV["CI"].present?
```

## Versão e ambiente

- Ambiente de teste Rails com RSpec, FactoryBot e DatabaseCleaner, este último com transação por exemplo via `around(:each)`.
- O eager load depende da variável de ambiente `CI`: ativo no CI, inativo localmente.
- A suíte completa tem 2253 exemplos. A seed da falha é 17813.
- `before(:all)` aparece em cerca de 115 arquivos de spec, a maioria com limpeza manual em `after(:all)`.
- Versões de Ruby, Rails, RSpec, DatabaseCleaner e banco de dados: Não informado na issue original.