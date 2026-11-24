## Resumo

`User#name` é definido uma única vez, quando o usuário do aluno é criado. Alterações posteriores em `Student#name` não chegam a `users.name`. Assim que o nome do aluno é editado pela primeira vez, os dois campos passam a divergir e continuam divergentes.

O título da issue também cita `Professor#name`, mas o corpo descreve apenas o caso de `Student`.

Segundo a issue, `Enrollment#create_user!` (`app/models/enrollment.rb:239`) é o único ponto de `app/` que define `User#name` a partir de `Student#name`. Esse método roda como `after_create` da matrícula (`app/models/enrollment.rb:56`) e copia o valor de `student.name` naquele momento. Não existe callback que propague alterações posteriores de `students.name` para `users.name`.

Relacionada à #658 (normalizar a caixa do nome ao mapear candidatura para aluno), mas independente dela. A #658 trata da entrada do nome em caixa alta. Esta issue trata da propagação de qualquer correção posterior, seja de caixa, sobrenome, acento ou typo.

## Passos para reproduzir

Sequência reconstruída pelo `paper_trail` de um aluno em produção. O nome foi substituído por um exemplo sintético.

1. Crie um aluno a partir do módulo de admissão, com o nome copiado da candidatura em caixa alta: `JOAO CARLOS DOS SANTOS` (13:34:43).
2. Salve a matrícula do aluno. O `after_create` executa `create_user!`, que convida o usuário com o mesmo nome em caixa alta (13:34:43).
3. Corrija `students.name` para `Joao Carlos dos Santos` (13:35:40).
4. Verifique `users.name` do usuário associado.

A janela entre a criação do usuário e a correção do nome vai de segundos a minutos. Segundo a issue, quase toda correção de nome cai nessa janela.

## Comportamento observado

`users.name` continua `JOAO CARLOS DOS SANTOS` indefinidamente, enquanto `students.name` passa a ser `Joao Carlos dos Santos`.

**Impacto medido:**

| instância | usuários com nome em caixa alta | total de usuários com nome |
|---|---|---|
| A | 22 | 853 |
| B (dados legados importados em massa) | 252 | 354 |

Na instância A, 30 dos 31 alunos vindos de candidatura em caixa alta tiveram o nome corrigido na tabela `students`, mas 22 usuários mantiveram a caixa alta original. Ou seja, hoje o dado incorreto está em `users`, e não em `students`.

**Onde o nome divergente aparece** (pontos verificados no código pelo autor):

- Templates de e-mail do Devise em `app/views/devise/mailer/`, todos iniciando com `{{ user.name }}`: `invitation_instructions`, `confirmation_instructions`, `reset_password_instructions`, `password_change`, `email_changed`, `unlock_instructions`. O convite recebido pelo aluno já sai com o nome errado.
- Autoria de comentários de inscrição via `comment.user.name`:
  - `app/views/enrollment_requests/_enrollment_request_comments_form_column.html.erb:21`
  - `app/views/student_enrollment/_enroll_comments.html.erb:16`
- `{{ user.name }}` nos e-mails de inscrição:
  - `app/views/student_enrollment/mailer/email_to_student.text.liquid:43`
  - `app/views/student_enrollment/mailer/email_to_advisor.text.liquid:43`
  - `app/views/enrollment_requests/mailer/email_to_student.text.liquid:19`
- `Report#to_label` (`app/models/report.rb:12`)
- `UserRole#to_label` (`app/models/user_role.rb:13`)
- Pendências de admissão (`app/models/admissions/admission_application.rb:338`)

## Comportamento esperado

Depois que `Student#name` é alterado, o `User` associado deve refletir o novo nome. Isso vale para correções de caixa, troca de sobrenome, correção de acento e typo. O autor considera `Student#name` a fonte de verdade do nome.

## Stack trace / saída de erro

Não informado na issue original.

## Caso de teste

A issue não traz código de teste. O cenário mínimo derivado dos passos acima é:

1. Criar um aluno com nome `JOAO CARLOS DOS SANTOS` e um e-mail.
2. Criar uma matrícula para esse aluno, o que dispara `create_user!` e cria o `User` com `name = "JOAO CARLOS DOS SANTOS"`.
3. Atualizar `student.name` para `Joao Carlos dos Santos`.
4. Recarregar o usuário associado e verificar `user.name`.
   - **Esperado:** `Joao Carlos dos Santos`
   - **Atual:** `JOAO CARLOS DOS SANTOS`

## Exemplo de código

Trecho de `Enrollment#create_user!` (`app/models/enrollment.rb:239`), que cria o usuário com uma cópia de `student.name`:

```ruby
user = User.invite!({
  email: student.first_email,
  name: student.name,
  roles: [role],
}, current_user) do |invitable|
  invitable.skip_confirmation!
end
```

## Versão e ambiente

- Versão: não informada na issue original.
- Ambiente: produção, com dados observados em duas instâncias (A e B; a B com dados legados importados em massa).
- Componentes mencionados: `paper_trail` (histórico de versões) e Devise (convites e e-mails de usuário).