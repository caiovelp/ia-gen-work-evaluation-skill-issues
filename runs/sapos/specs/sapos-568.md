# Spec: Corrigir a tela de pendências para turmas de Pesquisa de Tese e Pesquisa de Dissertação

## Premissas
1. O sistema é de gestão acadêmica de pós-graduação. A "tela de pendências" lista as turmas em que o professor ainda precisa lançar resultados.
2. Algumas disciplinas avaliam o aluno apenas por aprovação/reprovação, sem nota. São elas "Pesquisa de Tese" e "Pesquisa de Dissertação".
3. Nessas turmas a interface já impede o lançamento de nota e permite apenas aprovação/reprovação. A issue diz que "esse tipo de turma não permite lançamento de nota".
4. Hoje a pendência é calculada pela ausência de nota lançada para os alunos. A issue apresenta isso como hipótese ("possivelmente"), ainda não confirmada.
5. Nas turmas comuns, a pendência deve continuar sendo calculada como hoje.
6. Uma turma do tipo aprovação/reprovação deve sair das pendências quando todos os seus alunos tiverem aprovação ou reprovação lançada.
7. Existe no sistema alguma forma de identificar que uma disciplina não recebe nota, como um atributo, um tipo ou o código da disciplina. Essa forma ainda não foi identificada.

## Objetivo
Corrigir um falso positivo na tela de pendências. As turmas de Pesquisa de Tese e de Pesquisa de Dissertação continuam aparecendo como pendentes mesmo depois que o professor lança aprovação/reprovação para os alunos. A causa provável é que a verificação exige nota, e esse tipo de turma não aceita nota.

**Usuário:** professor (e possivelmente coordenação/secretaria) que consulta a tela de pendências.

**Comportamento esperado:**
- Nas turmas cujo critério de avaliação é só aprovação/reprovação, a pendência considera apenas o lançamento de aprovação/reprovação. A nota é ignorada.
- Se algum aluno dessas turmas estiver sem aprovação/reprovação lançada, a turma continua aparecendo como pendente.
- As turmas com lançamento de nota mantêm o comportamento atual.

## Stack Tecnológica
Não informado na issue original.

## Comandos
Não informado na issue original.
- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto
Não informado na issue original. Ainda é preciso localizar a lógica que monta a tela de pendências e onde fica o tipo de avaliação da disciplina.

## Estilo de Código
Não informado na issue original.

## Estratégia de Testes
O framework e a localização dos testes não foram informados na issue original. Cenários mínimos a cobrir:
- Turma de Pesquisa de Tese com aprovação/reprovação lançada para todos os alunos: **não** aparece nas pendências.
- Turma de Pesquisa de Dissertação com aprovação/reprovação lançada para todos os alunos: **não** aparece nas pendências.
- Turma de Pesquisa de Tese ou Dissertação com algum aluno sem aprovação/reprovação: **aparece** nas pendências.
- Turma comum (com nota) com alunos sem nota: **aparece** nas pendências, como hoje.
- Turma comum com todas as notas lançadas: **não** aparece nas pendências, como hoje.

## Limites
- **Sempre:** manter o comportamento atual das pendências para as turmas comuns. Identificar o tipo de turma por um atributo do sistema, se existir, e não por texto do nome. Adicionar testes de regressão para os cenários acima.
- **Perguntar antes:** alterar o esquema do banco, como criar um campo para indicar disciplina sem nota. Alterar regras de lançamento de notas ou de aprovação/reprovação. Fazer o mesmo ajuste em outras telas ou relatórios que também dependam de nota.
- **Nunca:** gravar notas fictícias nas turmas de pesquisa para "resolver" a pendência. Alterar dados históricos sem aprovação. Remover testes existentes.

## Critérios de Sucesso
- Depois que o professor lança aprovação/reprovação para todos os alunos de uma turma de Pesquisa de Tese ou de Pesquisa de Dissertação, a turma deixa de aparecer na tela de pendências.
- Essas turmas continuam aparecendo enquanto algum aluno estiver sem aprovação/reprovação.
- A tela de pendências não muda para as turmas que recebem nota.
- Os testes automatizados que cobrem esses cenários passam.

## Perguntas em Aberto
1. Confirmar a causa: a pendência é mesmo calculada pela ausência de nota? A issue diz "possivelmente".
2. Como o sistema identifica que uma disciplina não recebe nota? Existe um atributo ou tipo próprio, ou é preciso usar o código ou nome da disciplina?
3. Só essas duas disciplinas avaliam apenas por aprovação/reprovação, ou existem outras (por exemplo, estágio, seminários, exame de qualificação) que deveriam seguir a mesma regra?
4. A pendência dessas turmas deve exigir mais alguma coisa além de aprovação/reprovação, como frequência ou conceito?
5. Quem vê a tela de pendências: só o professor, ou também a coordenação e a secretaria? O ajuste vale para todos os perfis?
6. Outras telas ou relatórios (fechamento de período, histórico, relatórios de lançamento) usam a mesma lógica de "nota ausente" e também deveriam ser corrigidos?
7. As turmas antigas que hoje aparecem indevidamente devem sair das pendências automaticamente depois da correção, ou é preciso algum tratamento de dados?