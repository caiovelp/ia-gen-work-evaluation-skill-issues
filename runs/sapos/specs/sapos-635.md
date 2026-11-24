# Spec: Tratar token de confirmação inexistente em `Users::ConfirmationsController#show` sem erro 500

## Premissas

1. A aplicação é Rails e usa Devise para confirmação de e-mail, com o módulo `confirmable` e a opção `reconfirmable` ativos. Isso se infere do controller, de `super` e da menção a `reconfirmable`.
2. A interface está em pt-BR. A mensagem esperada é a tradução do Devise para token inválido ("Token de confirmação inválido").
3. `User` tem associação com `student` e/ou `professor`. O bloco passado a `super` propaga o novo e-mail a esses registros quando a confirmação dá certo.
4. O bloco de propagação já tem a guarda `user.errors.empty?`. Por isso ele não roda quando o Devise rejeita o token. Isso vem da issue; o bloco não foi visto por completo.
5. O comportamento esperado para token inválido é o padrão do Devise já configurado na aplicação. Não há mensagem, status ou redirecionamento customizado.
6. A mudança fica restrita ao trecho anterior a `super` em `show`. O caminho feliz (token válido) não muda.
7. A issue não trata o caso como vulnerabilidade: não há vazamento de dados nem escalonamento de privilégio. A classificação é robustez/UX.

## Objetivo

Hoje, ao acessar o link de confirmação com um token que não corresponde a nenhum usuário, o usuário vê uma tela de erro 500. A causa é um `NoMethodError` em `nil.email`, na linha que lê `user.email` antes de `super`, em `app/controllers/users/confirmations_controller.rb:16-17`.

O objetivo é que, nesse cenário, o fluxo siga para o Devise. O Devise deve então exibir sua mensagem padrão de token inválido.

**Usuário afetado:** usuário (student/professor) que pediu troca de e-mail e acessa um link de confirmação que não é mais válido. Exemplos: o mesmo link reaberto após a confirmação, um link antigo ou uma URL com `confirmation_token` inexistente.

**Critérios de aceitação (histórias):**
- Como usuário que já confirmou a troca de e-mail, ao clicar de novo no mesmo link, vejo uma mensagem amigável do Devise, e não uma página de erro 500.
- Como qualquer visitante, ao acessar a rota de confirmação com um `confirmation_token` inexistente, vejo a mensagem de token inválido do Devise.
- Como usuário com token válido, a confirmação da troca de e-mail e a propagação do novo e-mail para o `student`/`professor` associado continuam funcionando como hoje.

**Correção sugerida na issue (a validar, não implementada aqui):** proteger a leitura com navegação segura (`user&.email`), deixando o `super` do Devise tratar o erro.

## Stack Tecnológica

- Ruby on Rails, com versão não informada na issue original.
- Devise (`confirmable` + `reconfirmable`), com versão não informada na issue original.
- Demais dependências: não informado na issue original.

## Comandos

Não informado na issue original. Comandos de build, teste, lint e servidor de desenvolvimento são desconhecidos.

## Estrutura do Projeto

Apenas o que a issue cita:

```
app/controllers/users/confirmations_controller.rb → Controller customizado de confirmação do Devise (Users::ConfirmationsController)
```

- Modelos citados: `User`, `student`, `professor`. Os caminhos dos arquivos não foram informados na issue original.
- Diretório de testes: não informado na issue original.

## Estilo de Código

Não informado na issue original. O único trecho disponível é o código atual descrito na issue:

```ruby
def show
  user = User.find_by(confirmation_token: params[:confirmation_token])
  email_before = user.email   # user pode ser nil
  super do |user|
    ...
```

Convenções de nomenclatura, formatação e linter (ex.: RuboCop): não informado na issue original.

## Estratégia de Testes

O framework de testes (RSpec ou Minitest) e a localização dos testes não foram informados na issue original.

Níveis sugeridos para este caso:
- **Teste de request/controller** para `GET` na rota de confirmação, cobrindo:
  1. `confirmation_token` inexistente: não pode haver 500. A resposta deve ser a de token inválido do Devise.
  2. Token já usado (reabrir o mesmo link após a confirmação): não pode haver 500.
  3. Token válido de troca de e-mail (`reconfirmable`): o e-mail do `User` é confirmado e o novo e-mail é propagado ao `student`/`professor` associado. Este é o teste de regressão do caminho feliz.
  4. Parâmetro `confirmation_token` ausente ou vazio: não pode haver 500, e nenhum registro pode ser alterado (ver Questões em Aberto).
- O teste do item 1 deve falhar antes da correção, reproduzindo o 500/`NoMethodError`, e passar depois dela.
- Expectativa de cobertura: não informado na issue original.

## Limites

- **Sempre:**
  - Preservar o comportamento do caminho feliz, incluindo a propagação do e-mail anterior/novo para `student`/`professor`.
  - Delegar ao Devise (`super`) a resposta para token inválido, sem duplicar mensagens nem lógica de erro.
  - Adicionar teste que reproduza o erro antes da correção.
- **Perguntar antes:**
  - Alterar a guarda `user.errors.empty?` ou a lógica de propagação dentro do bloco.
  - Customizar mensagem, status HTTP ou redirecionamento de token inválido.
  - Alterar configuração do Devise (`config/initializers/devise.rb`, locales) ou rotas.
  - Mudar o esquema do banco (ex.: colunas de confirmação).
- **Nunca:**
  - Engolir exceções genericamente (`rescue` amplo) para esconder o 500.
  - Expor na resposta se um token ou e-mail existe além do que o Devise já expõe por padrão.
  - Remover ou afrouxar a guarda que impede a propagação quando a confirmação falha.

## Critérios de Sucesso

1. `GET` na rota de confirmação com `confirmation_token=<valor inexistente>` não gera `NoMethodError` nem status 500.
2. Nesse caso, a resposta é a padrão do Devise para token inválido, com a mensagem localizada "Token de confirmação inválido" ou equivalente do locale configurado. O status e o template são os que o Devise da aplicação já usa (ver Questões em Aberto).
3. Reabrir um link de confirmação já usado não gera 500.
4. Com token inválido, nenhum `student`/`professor` tem o e-mail alterado.
5. Com token válido de troca de e-mail, o `User` é confirmado e o `student`/`professor` associado recebe o e-mail atualizado, exatamente como antes.
6. Os testes novos e os existentes da suíte passam.

## Questões em Aberto

1. **Token após a confirmação:** nesta aplicação e versão do Devise, o `confirmation_token` é realmente limpo após a confirmação? Se não for, reabrir o mesmo link encontra o usuário e o Devise responde "e-mail já confirmado", não "token inválido". Nesse caso o passo 3 da reprodução só gera 500 com tokens de fato inexistentes. Qual mensagem se espera em cada caso?
2. **Link expirado:** em Devise, um token expirado (`confirm_within`) normalmente ainda existe no registro. Nesse caso `find_by` encontra o usuário e não ocorre `nil.email`. O caso "link expirado" citado na issue gera 500 na prática, ou só tokens inexistentes geram? É preciso cobrir os dois em teste?
3. **`confirmation_token` ausente ou vazio:** `User.find_by(confirmation_token: nil)` pode retornar algum usuário cujo token é `nil`, como um usuário já confirmado. A guarda `user.errors.empty?` impede efeitos colaterais nesse caso? Vale tratar explicitamente esse cenário, que hoje talvez não gere 500 mas carrega um `user` não relacionado?
4. **Status HTTP esperado:** para token inválido, a aplicação espera o status padrão do Devise na versão em uso (200 ou 422, conforme `responder.error_status`) ou algum outro?
5. **Conteúdo completo do bloco `super do |user| ... end`:** onde e como `email_before` é usado? Há outro acesso a `user` ou `email_before` que também precise tolerar `nil`?
6. **Framework e local de testes:** RSpec ou Minitest? Existem testes atuais para `Users::ConfirmationsController`?
7. **Versões** de Ruby, Rails e Devise.
8. **Monitoramento:** há ocorrências deste 500 em ferramenta de erros (ex.: Sentry) que permitam validar a correção em produção?