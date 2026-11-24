## Resumo

`Admissions::FormAutocompletesController#form_field` repassa `params[:term]` sem validação para `Admissions::FormField.full_search_name`. Quando a requisição não traz o parâmetro `term`, `field` fica `nil` e a busca por substring executa `name.include?(nil)`. Isso levanta `TypeError`, e a requisição termina em HTTP 500 com envio de notificação de exceção por e-mail.

## Passos para reproduzir

1. Autentique-se na aplicação.
2. Faça a requisição abaixo sem o parâmetro `term`:
   ```
   GET /form_autocompletes/form_field
   ```
3. Observe a resposta e as notificações de exceção.

## Comportamento observado

- A requisição retorna HTTP 500.
- É levantado `TypeError` (`no implicit conversion of nil into String`) em `app/models/admissions/form_field.rb:276`.
- É enviada uma notificação de exceção por e-mail.

## Comportamento esperado

A ausência do parâmetro `term` não deve causar erro interno. A resposta deve ser uma lista vazia ou um erro de requisição inválida, e nenhuma notificação de exceção deve ser enviada.

## Stack trace / saída de erro

```
A TypeError occurred in form_autocompletes#form_field:
  no implicit conversion of nil into String
  app/models/admissions/form_field.rb:276:in `include?'
```

## Caso de teste

Caso mínimo, derivado da chamada feita pelo controller com `params[:term]` ausente:

```ruby
Admissions::FormField.full_search_name(
  field: nil,
  in_letter: false,
  substring: true,
  limit: 10
)
# Observado: TypeError (no implicit conversion of nil into String)
```

No nível da requisição: um `GET /form_autocompletes/form_field` autenticado e sem `term` não deve retornar HTTP 500.

## Exemplo de código

`app/controllers/admissions/form_autocompletes_controller.rb`:

```ruby
@form_fields = Admissions::FormField.full_search_name(
  field: params[:term],
  in_letter: params[:in_letter] || false,
  substring: true,
  limit: 10
)
```

`app/models/admissions/form_field.rb:276`:

```ruby
result << name if name.include?(field)
```

## Versão e ambiente

- Encontrado durante uma varredura de rotas no ambiente de homologação.
- O comportamento é idêntico no Rails 7.1 e no Rails 7.2, portanto não se trata de regressão causada pelo upgrade.
- Versões de Ruby e de outras dependências: não informadas na issue original.