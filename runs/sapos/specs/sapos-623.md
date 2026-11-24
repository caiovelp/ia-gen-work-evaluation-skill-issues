# Spec: Tratamento de `term` ausente em `form_autocompletes#form_field`

## Objetivo

Hoje `GET /form_autocompletes/form_field` retorna HTTP 500 quando a requisição autenticada não traz o parâmetro `term`.

O que acontece:

- `Admissions::FormAutocompletesController#form_field` repassa `params[:term]` sem validação para `Admissions::FormField.full_search_name`.
- Com `substring: true`, o método executa `name.include?(nil)` em `app/models/admissions/form_field.rb:276`.
- Isso levanta `TypeError: no implicit conversion of nil into String`.
- O erro também dispara uma notificação de exceção por e-mail.

O que queremos:

- Uma requisição sem `term` (ausente ou em branco) não pode gerar HTTP 500.
- Ela também não pode disparar notificação de exceção.
- A resposta deve ser previsível: uma lista vazia ou um erro de requisição inválida. A escolha está em Perguntas em Aberto.

Usuários afetados:

- Usuários autenticados que consomem o autocomplete de campos de formulário de admissões.
- Indiretamente, a equipe que recebe os e-mails de exceção.

Critérios de aceitação (histórias):

- Como usuário autenticado, ao chamar o endpoint sem `term`, recebo uma resposta não-500, sem que uma exceção seja registrada ou notificada.
- Como usuário autenticado, ao chamar o endpoint com `term` válido, o comportamento atual da busca continua igual.

## Premissas

1. O comportamento correto para `term` ausente ou em branco ainda não foi decidido entre duas opções:
   - (a) responder com lista vazia;
   - (b) responder com erro de requisição inválida (ex.: HTTP 400).

   A issue sugere as duas. Esta spec assume (a) como padrão provisório, por ser mais compatível com o uso típico de autocomplete. Precisa de confirmação.
2. Valor "em branco" (string vazia ou só espaços) recebe o mesmo tratamento que parâmetro ausente.
3. O formato atual da resposta do endpoint (JSON, HTML etc.) e o contrato com o front-end devem ser mantidos. A issue não informa o formato.
4. O parâmetro `in_letter` e o caminho `substring: false` estão fora do escopo principal. A issue só mostra a falha no caminho de substring. Ver Perguntas em Aberto.
5. A correção vale igualmente para Rails 7.1 e 7.2, já que o problema não é regressão de upgrade.
6. A exigência de autenticação do endpoint não muda.

## Stack Tecnológica

- Ruby on Rails. A issue confirma que o problema ocorre no Rails 7.1 e no 7.2.
- Versão do Ruby, framework de testes e demais dependências: Não informado na issue original.
- Mecanismo de notificação de exceção por e-mail (gem ou serviço): Não informado na issue original.

## Comandos

Não informado na issue original.

- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Servidor de desenvolvimento: desconhecido

## Estrutura do Projeto

Arquivos citados na issue:

```
app/controllers/admissions/form_autocompletes_controller.rb  → Controller com a action form_field
app/models/admissions/form_field.rb                          → Model com full_search_name (linha 276: include?)
```

- Localização dos testes (ex.: `spec/` ou `test/`): Não informado na issue original.
- Arquivo de rotas e definição exata da rota `/form_autocompletes/form_field`: Não informado na issue original.

## Estilo de Código

Não informado na issue original. Seguir as convenções já presentes nos arquivos citados.

Trecho atual do controller, como referência de estilo (citado na issue):

```ruby
@form_fields = Admissions::FormField.full_search_name(
  field: params[:term],
  in_letter: params[:in_letter] || false,
  substring: true,
  limit: 10
)
```

## Estratégia de Testes

- Framework (RSpec, Minitest etc.): Não informado na issue original.
- Níveis de teste esperados:
  - **Requisição/controller:** chamada autenticada a `GET /form_autocompletes/form_field` com:
    - `term` ausente;
    - `term` vazio (`""`);
    - `term` só com espaços;
    - `term` válido (regressão).

    Verificar o status HTTP e o corpo da resposta.
  - **Model/unidade:** se a normalização ficar em `full_search_name`, cobrir `field: nil` e `field: ""` com `substring: true`, confirmando que nenhum `TypeError` é levantado.
- Cobertura mínima esperada: Não informado na issue original.

## Limites

- **Sempre:**
  - Manter a exigência de autenticação do endpoint.
  - Preservar o resultado da busca para `term` válido.
  - Incluir testes que reproduzam o cenário da issue (sem `term`).
- **Perguntar antes:**
  - Mudar o contrato da resposta (status HTTP, formato do corpo).
  - Tornar `limit` configurável via parâmetro de requisição.
  - Alterar `full_search_name` de forma que afete outros chamadores.
  - Adicionar dependências.
- **Nunca:**
  - Silenciar o `TypeError` com `rescue` genérico.
  - Desativar a notificação de exceção para esconder o problema.
  - Remover ou afrouxar a autenticação da rota.

## Critérios de Sucesso

1. Sem `term`, a chamada autenticada a `GET /form_autocompletes/form_field` retorna status diferente de 500. O status e o corpo são os definidos na decisão da Premissa 1 (provisoriamente: sucesso com lista vazia).
2. O mesmo resultado vale para `term` vazio e para `term` só com espaços.
3. Nenhum desses cenários levanta `TypeError` nem gera notificação de exceção por e-mail.
4. Com `term` válido, os resultados, a ordem e o limite de 10 itens continuam iguais aos de hoje.
5. Há testes automatizados para os itens 1–4, e eles passam no Rails 7.1 e no 7.2 (ou na versão em uso, se só uma estiver ativa).

## Perguntas em Aberto

1. Para `term` ausente ou em branco, a resposta deve ser lista vazia (200) ou erro de requisição inválida (ex.: 400)? O front-end depende de algum desses comportamentos?
2. Onde deve ficar a correção?
   - No controller: guarda antes da busca.
   - Em `full_search_name`: normalizar `field` para string vazia.
   - Nos dois.

   Há outros chamadores de `full_search_name` que hoje passam `nil`?
3. Se a normalização for para string vazia em `full_search_name`, `name.include?("")` é verdadeiro para todo nome. Nesse caso a busca devolveria os primeiros N campos, não uma lista vazia. Esse é o comportamento desejado?
4. O caminho com `substring: false` também falha com `field` nil? Deve entrar no escopo?
5. Sobre o `limit` ("vale checar também o `limit`, que hoje vem fixo do controller"), o que se espera?
   - Mantê-lo fixo em 10?
   - Aceitá-lo como parâmetro, com validação e teto?
   - Ou só garantir que `full_search_name` trate um `limit` inválido?
6. `params[:in_letter]` também deve ser validado ou normalizado (ex.: string `"false"` vs. booleano)?
7. Qual é o formato da resposta do endpoint (JSON, HTML parcial) e qual é o contrato esperado pelo consumidor?
8. Qual framework de testes o projeto usa, e quais comandos rodam a suíte e o lint?