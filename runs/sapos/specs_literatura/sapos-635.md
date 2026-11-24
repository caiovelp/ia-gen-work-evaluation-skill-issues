## Resumo

Ao acessar o link de confirmação de e-mail com um token que não corresponde a nenhum usuário, a aplicação responde com **erro 500**. O esperado é a mensagem padrão do Devise para token inválido ("Token de confirmação inválido").

O problema está em `Users::ConfirmationsController#show` (`app/controllers/users/confirmations_controller.rb:16-17`). A action busca o usuário pelo token **antes** de chamar `super`. O objetivo é guardar o e-mail anterior e propagá-lo ao `student`/`professor` associado quando o usuário confirma uma troca de e-mail (`reconfirmable`). Se o token não existir, `find_by` retorna `nil` e a chamada `user.email` levanta `NoMethodError`.

Escopo segundo o autor: não é uma vulnerabilidade, pois não há vazamento de dados nem escalonamento de privilégios. É uma questão de robustez e UX. O caminho feliz, com token válido, não é afetado.

## Passos para reproduzir

1. Um usuário solicita a troca de e-mail e recebe o link de confirmação.
2. O usuário clica no link. A troca é confirmada e o token é consumido/limpo.
3. O usuário acessa o **mesmo link novamente**. Variantes equivalentes:
   - acessar um link expirado;
   - acessar qualquer URL de confirmação com `?confirmation_token=<valor inexistente>`.

## Comportamento observado

- `User.find_by(confirmation_token: ...)` retorna `nil`.
- A linha seguinte executa `nil.email` e levanta `NoMethodError`.
- O Rails responde com uma tela de **erro 500**.

## Comportamento esperado

O Devise deve exibir sua mensagem padrão e amigável para token inválido ("Token de confirmação inválido"), sem erro 500.

## Stack trace / saída de erro

A issue menciona apenas o tipo da exceção: `NoMethodError`, por chamada de `email` em `nil`, em `app/controllers/users/confirmations_controller.rb:16-17`. O stack trace completo e a mensagem de log não foram informados na issue original.

## Caso de teste

Caso de teste mínimo derivado dos passos de reprodução (o código do teste não foi informado na issue original):

- **Ação:** fazer uma requisição para a action `show` de `Users::ConfirmationsController` com `confirmation_token` igual a um valor que não corresponde a nenhum usuário.
- **Verificação:** a resposta não deve ser 500 e deve exibir a mensagem de token inválido do Devise.
- **Variante:** confirmar uma troca de e-mail com um token válido e repetir a mesma requisição com o mesmo token. O resultado esperado é o mesmo.

## Exemplo de código

Trecho de `app/controllers/users/confirmations_controller.rb` citado na issue:

```ruby
def show
  user = User.find_by(confirmation_token: params[:confirmation_token])
  email_before = user.email   # user pode ser nil
  super do |user|
    ...
```

## Versão e ambiente

Não informado na issue original. A issue indica apenas que a aplicação usa Rails e Devise com o módulo `reconfirmable`, sem informar versões.