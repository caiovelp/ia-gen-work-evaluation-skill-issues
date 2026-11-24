# Spec: Propagar alterações de `Student#name` (e `Professor#name`) para o `User` associado

## Objetivo

Hoje `users.name` é uma cópia de `students.name` tirada no momento da matrícula e nunca é atualizada depois. Queremos que o nome do usuário acompanhe o nome do aluno, para que correções posteriores apareçam nos lugares que exibem `user.name`.

**Situação atual:**
- `Enrollment#create_user!` (`app/models/enrollment.rb:239`) é o único ponto do `app/` que define `User#name` a partir de `Student#name`. Ele faz isso via `User.invite!` com `name: student.name`.
- `create_user!` roda em `after_create` da matrícula (`app/models/enrollment.rb:56`). O usuário nasce no momento em que a matrícula é salva.
- Nenhum callback propaga alterações posteriores de `students.name` para `users.name`. A partir da primeira edição do nome do aluno, os dois divergem para sempre.

**Caso típico (reconstruído pelo `paper_trail`):**
1. Um aluno vindo da admissão é criado com o nome em caixa alta.
2. O usuário é convidado com esse mesmo nome.
3. Segundos ou minutos depois, a secretaria corrige `students.name`.
4. `users.name` continua com o valor original.

**Impacto medido:**

| Instância | Usuários com nome em caixa alta | Total de usuários com nome |
|---|---|---|
| A | 22 | 853 |
| B (legado importado em massa) | 252 | 354 |

Na instância A, 30 dos 31 alunos vindos de candidatura em caixa alta tiveram o nome corrigido em `students`. Mesmo assim, 22 usuários mantiveram a caixa alta. O dado sujo hoje mora em `users`, não em `students`.

**Onde o nome divergente aparece:**
- Templates de e-mail do Devise em `app/views/devise/mailer/`, todos com `{{ user.name }}`: `invitation_instructions`, `confirmation_instructions`, `reset_password_instructions`, `password_change`, `email_changed`, `unlock_instructions`.
- Autoria de comentários de inscrição:
  - `app/views/enrollment_requests/_enrollment_request_comments_form_column.html.erb:21`
  - `app/views/student_enrollment/_enroll_comments.html.erb:16`
- E-mails de inscrição:
  - `app/views/student_enrollment/mailer/email_to_student.text.liquid:43`
  - `app/views/student_enrollment/mailer/email_to_advisor.text.liquid:43`
  - `app/views/enrollment_requests/mailer/email_to_student.text.liquid:19`
- `Report#to_label` (`app/models/report.rb:12`)
- `UserRole#to_label` (`app/models/user_role.rb:13`)
- Pendências de admissão (`app/models/admissions/admission_application.rb:338`)

**Quem se beneficia:**
- Alunos, que recebem e-mails e veem o próprio nome.
- Secretaria e orientadores, que veem a autoria de comentários, relatórios e papéis.

**Como é o sucesso:** qualquer correção de nome feita no aluno passa a valer para o usuário associado. Isso inclui caixa, sobrenome, acento e typo.

**Escopo:**
- Inclui o callback de propagação em `Student`.
- Inclui `Professor`, se confirmado (ver Perguntas em Aberto).
- Não inclui a limpeza dos dados já divergentes. Ela é operacional, por instância, e fica fora desta issue.
- Não inclui a normalização de caixa na entrada, que é tratada na #658. As duas issues são relacionadas, mas independentes.

**Correção proposta na issue:** um callback em `Student` que, ao detectar `saved_change_to_name?` e havendo `user` associado, atualize `user.name`.

## Premissas

1. `Student#name` é a fonte de verdade do nome. Se um usuário teve o nome editado manualmente e divergiu, a propagação sobrescreve esse valor. A issue sugere isso, argumentando que não há UI pensada para divergência intencional.
2. Só alterações por update interessam. Na criação do aluno, o usuário ainda não existe; ele é criado depois, pelo `after_create` da matrícula.
3. `Student` tem uma associação `user`, que pode ser nula. Quando for nula, a propagação não faz nada.
4. A aplicação é Ruby on Rails, usando Devise (com `devise_invitable`), `paper_trail` e Liquid. Isso é inferido dos trechos citados; as versões não são conhecidas.
5. A mesma lógica deve valer para `Professor#name`, já que o título da issue o menciona. Porém o corpo da issue não mostra como o usuário do professor é criado nem onde.
6. O caminho do convite (`create_user!`) continua como está. A correção atua apenas sobre alterações posteriores.

## Stack Tecnológica

Ruby on Rails, Devise com `devise_invitable` (`User.invite!`, `skip_confirmation!`), `paper_trail` e templates Liquid, todos inferidos dos trechos citados. As versões não foram informadas na issue original.

## Comandos

Não informado na issue original.

## Estrutura do Projeto

Apenas os caminhos citados na issue:

```
app/models/enrollment.rb                    → create_user! (l. 239), after_create (l. 56)
app/models/student.rb                       → validação changed_to_different_user (l. 36 e l. 101)
app/models/report.rb                        → Report#to_label (l. 12)
app/models/user_role.rb                     → UserRole#to_label (l. 13)
app/models/admissions/admission_application.rb → pendências de admissão (l. 338)
app/views/devise/mailer/                    → templates de e-mail do Devise
app/views/enrollment_requests/              → comentários e e-mails de inscrição
app/views/student_enrollment/               → comentários e e-mails de inscrição
```

Não foram informados:
- O local do model `Professor` e o fluxo de criação do seu usuário.
- O local dos testes.

## Estilo de Código

Não informado na issue original. O único trecho disponível é o de `create_user!`, reproduzido na própria issue.

## Estratégia de Testes

O framework e a localização dos testes não foram informados na issue original. Os níveis esperados, derivados dos critérios de sucesso, são:

- **Testes de model (`Student`)**
  - Alterar `name` de um aluno com usuário atualiza `user.name`.
  - Alterar outro atributo não toca em `user`.
  - Alterar `name` de um aluno sem usuário não gera erro.
- **Teste de regressão da validação `changed_to_different_user`**: a propagação não pode dispará-la indevidamente nem causar recursão.
- **Testes equivalentes para `Professor`**, se ele estiver no escopo.
- **Teste de integração (opcional)**: criar uma matrícula (o que gera o usuário via `create_user!`), alterar o nome do aluno e verificar que o usuário reflete o novo nome.

## Limites

- **Sempre:**
  - Tratar `Student#name` como fonte de verdade.
  - Propagar apenas quando o nome de fato mudou (`saved_change_to_name?`).
  - Não fazer nada quando não há `user` associado.
  - Cobrir com testes os casos com e sem usuário.
- **Perguntar antes:**
  - Pular validações ou callbacks do `User` (por exemplo, usar `update_column`).
  - Mudar o comportamento de versionamento do `paper_trail` para o `User`.
  - Alterar `Enrollment#create_user!`.
  - Incluir a normalização de caixa (escopo da #658).
- **Nunca:**
  - Fazer a limpeza de dados existentes dentro desta mudança.
  - Criar sincronização no sentido inverso (`User` → `Student`) sem decisão explícita.
  - Remover ou afrouxar a validação `changed_to_different_user`.

## Critérios de Sucesso

1. Ao salvar um `Student` existente com `name` alterado e `user` associado, `user.name` passa a ser igual ao novo `student.name`.
2. O critério 1 vale para qualquer tipo de alteração: caixa, sobrenome, acento e typo.
3. Ao salvar um `Student` sem alteração em `name`, o `User` associado não é modificado.
4. Ao salvar um `Student` com `name` alterado e sem `user` associado, não ocorre erro e nenhum `User` é criado.
5. Um `User` cujo nome divergia manualmente é sobrescrito pela alteração do nome do aluno, conforme a Premissa 1.
6. Não há recursão de callbacks. A validação `changed_to_different_user` continua se comportando como antes para trocas de usuário.
7. A criação de matrícula e o convite via `create_user!` continuam funcionando, com o nome do aluno no momento da criação.
8. Se `Professor` estiver no escopo, os critérios 1 a 6 valem para `Professor#name` e o seu `User` associado.

## Perguntas em Aberto

1. **`Professor`:** o título cita `Professor#name`, mas o corpo só trata de `Student`. `Professor` está no escopo?
   - Como e onde o usuário do professor é criado?
   - Professor e aluno podem compartilhar o mesmo `User`? Se sim, qual nome vence?
2. **`after_update` vs `after_save`:** a issue sugere que só o update interessa. Confirmar `after_update`. Avaliar também se a propagação deve ocorrer dentro da mesma transação (`after_update`) ou após o commit (`after_update_commit`).
3. **Falha ao salvar o `User`:** se `user.name` falhar por validação do `User`, o que deve acontecer?
   - Abortar o save do aluno?
   - Ignorar e registrar em log?
   - Usar `update!` para propagar o erro?
4. **Validações e auditoria:** a atualização do `User` deve passar pelas validações e callbacks normais e gerar versão no `paper_trail`? Ou deve ser uma escrita direta?
5. **Causa da recursão:** qual é exatamente o risco de recursão mencionado na issue? Existe hoje algum callback em `User` que escreva em `Student`?
6. **`changed_to_different_user`:** em que situação essa validação (`app/models/student.rb:36` e `:101`) poderia ser disparada pela propagação? E se o `user` estiver mudando no mesmo save em que o `name` muda, o nome deve ir para o novo usuário?
7. **Divergência intencional:** confirmar que não existe nenhum caso legítimo de `User#name` diferente de `Student#name`, por exemplo um nome social editado pelo próprio usuário. Se existir, isso afeta a Premissa 1.
8. **Comandos e testes:** quais são os comandos de teste, lint e build do projeto, e qual framework de testes é usado?