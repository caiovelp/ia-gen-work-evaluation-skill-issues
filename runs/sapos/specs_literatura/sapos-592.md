## Resumo
Ao cadastrar uma dissertação/tese cujo título contém um caractere Unicode (a letra grega sigma), o SAPOS exibe o erro "Incorrect String Value" e não conclui o cadastro. O problema ocorre com banco de dados MySQL.

## Passos para reproduzir
1. Usar o SAPOS com banco de dados MySQL.
2. Iniciar o cadastro de uma dissertação/tese.
3. Preencher o título com um texto que contenha o caractere sigma (por exemplo, "σ" ou "Σ").
4. Salvar o cadastro.

## Comportamento observado
O SAPOS apresenta o erro "Incorrect String Value" e a dissertação/tese não é cadastrada.

## Comportamento esperado
A dissertação/tese deveria ser cadastrada, e o título deveria ser salvo com o caractere Unicode (sigma) preservado.

## Stack trace / saída de erro
```
Incorrect String Value
```
(A issue original informa apenas essa mensagem. Não há stack trace completo.)

## Caso de teste
Não informado na issue original.

## Exemplo de código
Não informado na issue original.

## Versão e ambiente
- Banco de dados: MySQL (versão não informada)
- Versão do SAPOS: Não informado na issue original.