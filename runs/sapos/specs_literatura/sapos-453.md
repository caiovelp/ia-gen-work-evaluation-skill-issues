## Resumo
Nas telas que permitem editar o trancamento, a combo de seleção do ano de trancamento só oferece os 5 anos anteriores ao ano atual. Assim, não é possível escolher anos mais antigos. Além disso, ao editar um trancamento já existente cujo ano é anterior a esse intervalo, a combo de ano aparece em branco e não permite selecionar novamente o ano que estava cadastrado.

## Passos para reproduzir
1. Acessar uma tela que permite editar o trancamento.
2. Abrir a combo de seleção do ano de trancamento e verificar os anos disponíveis.
3. Editar um trancamento já existente cujo ano cadastrado seja anterior aos 5 anos que antecedem o ano atual.
4. Observar o valor exibido na combo de ano.

(A issue original não identifica quais telas específicas apresentam o problema.)

## Comportamento observado
- A combo de ano lista apenas os 5 anos anteriores ao ano atual, e não é possível escolher anos mais antigos.
- Ao editar um trancamento existente com ano anterior a esse intervalo, a combo de ano fica em branco e o ano cadastrado não pode ser selecionado novamente.

## Comportamento esperado
A issue original não descreve o comportamento esperado de forma explícita. Pelo relato, espera-se que:
- seja possível selecionar anos anteriores ao limite de 5 anos;
- ao editar um trancamento existente, a combo de ano exiba e permita manter o ano que já estava cadastrado.

## Stack trace / saída de erro
Não informado na issue original.

## Caso de teste
Não informado na issue original.

Um caso de teste derivado do relato seria: editar um trancamento cujo ano cadastrado seja anterior aos 5 anos que antecedem o ano atual e verificar se a combo de ano exibe esse ano já selecionado e permite mantê-lo.

## Exemplo de código
Não informado na issue original.

## Versão e ambiente
Não informado na issue original.