## Resumo
Ao lançar nota em uma turma com nome muito grande, ocorre o erro `Mysql2::Error: Data too long for column 'subject' at row 1`. Segundo a análise do relator, o erro acontece porque o nome da turma é usado no assunto (subject) do e-mail enviado ao aluno, ao professor e ao orientador. Com um nome longo, o assunto ultrapassa o tamanho máximo da coluna `subject`.

## Passos para reproduzir
1. Ter uma turma cujo nome seja muito grande. O tamanho exato do nome não foi informado.
2. Tentar lançar nota nessa turma.
3. Observar o erro.

## Comportamento observado
O lançamento de nota falha com o erro `Mysql2::Error: Data too long for column 'subject' at row 1`. Segundo o relator, a causa é o uso do nome da turma no assunto do e-mail de notificação enviado ao aluno, ao professor e ao orientador.

## Comportamento esperado
O lançamento de nota deve ser concluído sem erro, mesmo quando o nome da turma é muito grande.

## Stack trace / saída de erro
```
Mysql2::Error: Data too long for column 'subject' at row 1
```
A stack trace completa não foi informada na issue original.

## Caso de teste
Não informado na issue original.

## Exemplo de código
Não informado na issue original.

## Versão e ambiente
Não informado na issue original. O erro indica apenas o uso de MySQL por meio da gem `mysql2`.