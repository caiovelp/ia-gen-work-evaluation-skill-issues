## Resumo
Cancelar automaticamente as inscrições em disciplinas quando a matrícula de um aluno for trancada.

## Descrição
Hoje, ao trancar a matrícula de um aluno, as inscrições dele nas disciplinas continuam ativas e precisam ser canceladas manualmente. A solicitação é que essas inscrições sejam canceladas automaticamente no momento do trancamento.

## Versão do produto
Não informado na issue original.

## Justificativa
O cancelamento manual das inscrições após cada trancamento é um trabalho adicional. Ele deveria ser desnecessário, já que o trancamento implica que o aluno não cursará as disciplinas.

## Caso de uso ou cenário
1. Um usuário efetua o trancamento da matrícula de um aluno.
2. Hoje, o usuário precisa depois cancelar manualmente cada inscrição do aluno nas disciplinas.
3. Com a funcionalidade, as inscrições seriam canceladas automaticamente, sem esse passo manual.

## Solução possível
Ao trancar uma matrícula, o sistema deve cancelar automaticamente todas as inscrições em disciplinas associadas a ela.