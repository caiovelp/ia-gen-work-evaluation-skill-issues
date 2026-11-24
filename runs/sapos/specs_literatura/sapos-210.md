## Resumo
Registrar a data de credenciamento do professor, mantendo o histórico de credenciamentos.

## Descrição
Adicionar a data de credenciamento do professor. Um professor pode ser credenciado, descredenciado e credenciado novamente, sem limite de vezes. Por isso, não basta guardar uma única data: é preciso manter o histórico desses credenciamentos.

## Versão do produto
Não informado na issue original.

## Justificativa
Um professor pode passar por vários ciclos de credenciamento e descredenciamento. Guardar apenas uma data perderia as informações dos períodos anteriores, por isso é necessário manter o histórico. A issue não diz por que a data de credenciamento é necessária para o sistema ou para seus usuários.

## Caso de uso ou cenário
Um professor é credenciado em uma data. Depois, é descredenciado. Mais tarde, é credenciado novamente. Esse ciclo pode se repetir indefinidamente, e cada credenciamento deve ficar registrado no histórico do professor.

## Possível solução
A issue sugere guardar o histórico de credenciamentos do professor, com a data de cada credenciamento, em vez de uma única data. A issue não detalha como esse histórico seria implementado.