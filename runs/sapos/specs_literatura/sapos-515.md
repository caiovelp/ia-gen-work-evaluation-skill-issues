## Resumo

Ao avaliar condições com `form_condition`, os valores de campos de consolidação são tratados como string em vez de número. Por isso, comparações numéricas retornam resultados incorretos.

## Passos para reproduzir

1. Crie um campo de consolidação que calcule a "Nota final" e que, para os dados informados, resulte no valor `10`.
2. Defina um `form_condition` com a condição `Nota final > 6`.
3. Faça o sistema avaliar a condição.

## Comportamento observado

O sistema compara os valores como strings (`"10" > "6"`). A condição retorna **falso**.

## Comportamento esperado

O valor da consolidação deve ser tratado como número (`10 > 6`). A condição deve retornar **verdadeiro**.

## Stack trace / saída de erro

Não informado na issue original.

## Caso de teste

Caso de teste mínimo derivado do exemplo da issue:

- **Dado** um campo de consolidação "Nota final" cujo valor calculado é `10`
- **E** um `form_condition` com a condição `Nota final > 6`
- **Quando** a condição é avaliada
- **Então** o resultado deve ser verdadeiro (atualmente é falso)

## Exemplo de código

Condição usada no exemplo da issue:

```
Nota final > 6
```

Comparação efetivamente realizada pelo sistema, segundo a issue:

```
"10" > "6"
```

## Versão e ambiente

Não informado na issue original.