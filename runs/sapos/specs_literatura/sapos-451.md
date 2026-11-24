## Resumo
A ordenação alfabética das disciplinas no quadro de horários não trata corretamente letras acentuadas. Disciplinas cujo nome começa com uma letra acentuada (por exemplo, _Á_) aparecem no final do quadro, em vez de serem ordenadas junto com as que começam com a letra sem acento correspondente (por exemplo, _A_).

## Passos para reproduzir
1. Ter no quadro de horários disciplinas cujos nomes começam com a mesma letra, com e sem acento, por exemplo:
   - _Análise de Imagens_
   - _Álgebra Linear_
2. Visualizar o quadro de horários, cujas disciplinas são exibidas em ordem alfabética.
3. Observar a posição de cada disciplina no quadro.

## Comportamento observado
- _Análise de Imagens_ aparece entre as primeiras disciplinas do quadro, por começar com _A_.
- _Álgebra Linear_ aparece no final do quadro, por começar com _Á_.

O acento de uma letra altera a posição da disciplina na ordem alfabética.

## Comportamento esperado
A ordenação alfabética deve tratar letras acentuadas junto com as letras sem acento correspondentes. Assim, _Álgebra Linear_ deve aparecer entre as disciplinas que começam com _A_, e não no final do quadro.

## Stack trace / saída de erro
Não informado na issue original.

## Caso de teste
Entrada (nomes de disciplinas no quadro de horários):
- _Análise de Imagens_
- _Álgebra Linear_

Resultado atual: _Álgebra Linear_ aparece no final do quadro, depois das disciplinas que começam com outras letras.

Resultado esperado: _Álgebra Linear_ e _Análise de Imagens_ aparecem juntas, entre as disciplinas iniciadas por _A_.

## Exemplo de código
Não informado na issue original.

## Versão e ambiente
Não informado na issue original.