# Spec: Guardas defensivas em `Ability` para associações `professor`/`student` ausentes

## Objetivo

Endurecer `app/models/ability.rb` para que as regras de autorização nunca sejam montadas a partir de uma associação `nil` (`user.professor` ou `user.student`). Isso é proteção defensiva, não correção de falha ativa. Hoje o caminho não é alcançável pela interface, por três camadas independentes descritas na issue. A camada 2, o rollback transacional do `ActiveScaffold::Actions::Update#update_save`, depende de uma gem que está sendo atualizada na #621. Se essa camada sumir, nenhum teste vai acusar.

**Problemas a tratar:**

1. **`initialize_professors`** monta condições a partir de `user.professor` sem guarda:
   ```ruby
   can :update, Grant, professor: user.professor
   can :update, Paper, owner: user.professor
   ```
   Com `user.professor == nil`, a condição vira `professor: nil` / `owner: nil`. Isso **concede** acesso a registros órfãos em vez de negar. `initialize_courses`, no mesmo arquivo, já usa `if user.professor.present?`.
2. **Regras mortas:** `can :destroy, PaperProfessor, paper: { owner: nil }` e `can :destroy, PaperStudent, paper: { owner: nil }`. A issue as considera inalcançáveis porque `Paper#owner` é `optional: false`.
3. **`initialize_documents`:** `generate_assertion` chama `user.student.enrollments` sem verificar `user.student`. Com `student` nil, a falha seria `NoMethodError` (HTTP 500), não concessão.

**Usuários afetados:** usuários com papel de professor ou aluno cuja associação correspondente esteja ausente. Esse estado hoje não é alcançável pela interface.

**Como é o sucesso:** com a associação ausente, a ability nega a permissão de forma determinística, sem conceder nada e sem lançar exceção. Com a associação presente, o comportamento atual se mantém. Tudo isso fica coberto pelo spec da #629.

**Critérios de aceitação (resumo):**
- `initialize_professors` só registra as regras de `Grant`/`Paper` quando `user.professor.present?`.
- As duas regras `can :destroy, ..., paper: { owner: nil }` deixam de existir.
- `initialize_documents` não acessa `user.student.enrollments` quando `user.student` é nil.
- Há testes para os casos nil e presente no spec da #629.

## Premissas

1. A biblioteca de autorização é a CanCan/CanCanCan. A inferência vem da sintaxe `can :acao, Modelo, condicoes` e de `can?`, mas a issue não nomeia a gem nem a versão.
2. A guarda deve seguir exatamente o padrão já usado em `initialize_courses` (`if user.professor.present?`), sem introduzir abstração nova.
3. Com `user.professor` nil, o comportamento desejado é **não ter** as permissões `:update` em `Grant`/`Paper` vindas desse bloco. Não deve haver regra alternativa nem exceção.
4. Com `user.student` nil, o comportamento desejado para `generate_assertion` é **negar** a permissão, e não lançar exceção.
5. As regras `can :destroy, PaperProfessor/PaperStudent, paper: { owner: nil }` não servem a nenhum fluxo legítimo. A premissa vale apenas para registros persistidos. Para objetos em memória ainda não salvos, ver Perguntas em Aberto.
6. O "spec da #629" é um arquivo de testes já existente ou em andamento para `Ability`. O caminho e o framework de testes não foram informados.
7. As camadas 1 e 3 descritas na issue continuam verdadeiras: `professors_controller.rb` não expõe a coluna `user`, e `Grant#professor` e `Paper#owner` são `optional: false`.
8. A mudança não altera o banco, as migrações, os controllers nem a configuração do active_scaffold.

## Stack Tecnológica

- Ruby on Rails. A inferência vem de `app/models/`, `has_one` e `ActiveRecord::Rollback`. Versões não informadas na issue original.
- active_scaffold, com atualização em andamento na #621. Versão não informada na issue original.
- Biblioteca de autorização: provavelmente CanCan/CanCanCan (ver Premissa 1). Versão não informada na issue original.
- Framework de testes: não informado na issue original.

## Comandos

Não informado na issue original.

- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Só os caminhos citados na issue:

```
app/models/ability.rb        → Arquivo alvo: initialize_professors, initialize_courses, initialize_documents
professors_controller.rb     → Citado como camada 1 (não expõe a coluna `user`); caminho completo não informado
```

O local do spec da #629 não foi informado na issue original.

## Estilo de Código

O padrão a seguir é o já existente em `initialize_courses`, conforme descrito na issue: `if user.professor.present?` protegendo o trecho. O trecho exato de `initialize_courses` não foi reproduzido na issue. A guarda deve ter a mesma forma (modificador `if` ou bloco), para que o arquivo fique consistente consigo mesmo. Outras convenções de estilo não foram informadas na issue original.

## Estratégia de Testes

Os testes ficam no spec da #629. Framework e local não foram informados na issue original. Nível: teste unitário da ability, instanciando `Ability` com um usuário construído.

Casos a cobrir:

| # | Cenário | Esperado |
|---|---|---|
| 1 | Usuário professor com `user.professor` presente; `Grant` do próprio professor | `can?(:update, grant)` é `true` |
| 2 | Usuário professor com `user.professor` presente; `Grant` de outro professor | `can?(:update, grant)` é `false` |
| 3 | Usuário professor com `user.professor` presente; `Paper` cujo `owner` é o próprio professor / de outro | `true` / `false` |
| 4 | Usuário com papel de professor e `user.professor` nil; `Grant`/`Paper` de outro | `can?(:update, ...)` é `false` |
| 5 | Usuário com papel de professor e `user.professor` nil; `Grant`/`Paper` com `professor`/`owner` nil, construído em memória | `can?(:update, ...)` é `false`. **Este é o caso que distingue a guarda da camada 3.** |
| 6 | `Ability.new(user)` com `user.professor` nil | Não lança exceção |
| 7 | Usuário com `user.student` nil avaliando `generate_assertion` | Sem `NoMethodError`; permissão negada |
| 8 | Usuário com `user.student` presente avaliando `generate_assertion` | Comportamento atual preservado (detalhes da regra não informados na issue original) |
| 9 | `PaperProfessor`/`PaperStudent` ligados a `Paper` com `owner` nil, em memória | `can?(:destroy, ...)` é `false` após a remoção das regras (ver Perguntas em Aberto) |

Os casos 4 e 5 passam hoje pela camada 3 só no caso 4. O caso 5 é o que garante que a proteção não depende da validação do modelo.

Expectativa de cobertura: não informado na issue original.

## Limites

- **Sempre:**
  - Manter o comportamento atual para usuários com associação presente.
  - Seguir o padrão de guarda já usado em `initialize_courses`.
  - Rodar a suíte da `Ability` antes de concluir.
  - Restringir a mudança a `app/models/ability.rb` e ao spec da #629.
- **Perguntar antes:**
  - Alterar outras regras de `Ability` além das três listadas.
  - Mexer em controllers, na configuração do active_scaffold ou em validações de modelo (`optional: false`).
  - Acoplar a mudança à #621.
  - Remover regras cuja necessidade não seja comprovadamente nula (ver pergunta sobre objetos em memória).
- **Nunca:**
  - Substituir a guarda por uma regra que conceda acesso quando a associação é nil.
  - Reintroduzir comportamento de 500 no lugar de negação.
  - Remover ou afrouxar testes existentes da `Ability` sem aprovação.

## Critérios de Sucesso

1. Em `app/models/ability.rb`, as duas regras de `initialize_professors` (`Grant`/`professor` e `Paper`/`owner`) só são registradas quando `user.professor.present?`.
2. Com `user.professor` nil, `can?(:update, x)` é `false` para qualquer `Grant`/`Paper`, inclusive instâncias em memória com `professor`/`owner` nil.
3. As regras `can :destroy, PaperProfessor, paper: { owner: nil }` e `can :destroy, PaperStudent, paper: { owner: nil }` não existem mais no arquivo.
4. Com `user.student` nil, avaliar a permissão de `generate_assertion` não lança `NoMethodError` e resulta em negação.
5. Com as associações presentes, todas as permissões verificadas nos casos 1–3 e 8 têm o mesmo resultado de antes da mudança.
6. Os casos da tabela de testes estão no spec da #629 e passam.
7. Nenhum arquivo fora de `app/models/ability.rb` e do spec da #629 foi alterado.

## Perguntas em Aberto

1. **Objetos não persistidos e as regras de `destroy`:** as regras `paper: { owner: nil }` podem estar servindo a algum fluxo com `Paper` ainda não salvo, por exemplo a remoção de linhas aninhadas (`PaperProfessor`/`PaperStudent`) num formulário de criação do active_scaffold antes de o `owner` ser atribuído. `optional: false` impede a persistência, mas não impede a checagem `can?` sobre um objeto em memória. Isso precisa ser confirmado antes da remoção.
2. Em que bloco ou papel essas duas regras de `destroy` estão definidas: em `initialize_professors` ou em outro método? A issue não diz.
3. Para `generate_assertion` com `user.student` nil, o resultado esperado é simplesmente não registrar a regra (negação)? Ou existe algum outro papel que deveria manter acesso por outro caminho?
4. A forma exata da regra de `generate_assertion` (bloco, condição em hash, escopo de `enrollments`) não foi mostrada. A guarda deve envolver só essa regra ou todo o conteúdo de `initialize_documents`?
5. Qual é o caminho e o framework do spec da #629, e ele já existe ou será criado junto?
6. Deve-se também acrescentar, nesta issue ou em outra, um teste de regressão para a camada 2 (rollback do `update_save` ao limpar o `record_select` de professor)? É justamente a camada ameaçada pela #621. Ou isso fica fora de escopo?
7. Esta mudança deve ser mergeada antes da #621, para garantir a proteção durante a atualização do active_scaffold?
8. Há outros métodos `initialize_*` em `ability.rb` que usam `user.professor` ou `user.student` sem guarda e que deveriam entrar no mesmo pacote? A issue afirma que "a guarda falta só aqui" para professor, mas não diz o mesmo para student.