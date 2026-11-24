## Resumo

Ao excluir um Aluno ou Professor associado a um usuário, o sistema não faz nenhum tratamento. Com isso, o usuário fica com o role "Aluno" ou "Professor" sem estar ligado a uma instância real correspondente. Isso viola a regra de que todo usuário com esses roles deve estar obrigatoriamente vinculado a um Aluno ou Professor existente.

## Passos para reproduzir

1. Tenha um usuário com o role "Aluno" (ou "Professor") associado a uma instância de Aluno (ou Professor).
2. Exclua essa instância de Aluno (ou Professor).
3. Verifique o usuário associado.

## Comportamento observado

A exclusão ocorre sem nenhum tratamento da associação. O usuário mantém o role "Aluno"/"Professor" sem estar ligado a uma instância real. A issue original traz uma captura de tela do problema (https://github.com/user-attachments/assets/f0346ba0-f3e3-44b1-8894-fc08edc1385f), mas o conteúdo dela não está descrito em texto.

## Comportamento esperado

A exclusão de um Aluno ou Professor ligado a um usuário deve ser tratada. Nenhum usuário pode ficar com o role "Aluno" ou "Professor" sem estar vinculado a uma instância real correspondente.

## Stack trace / saída de erro

Não informado na issue original.

## Caso de teste

Não informado na issue original.

## Exemplo de código

Não informado na issue original.

## Versão e ambiente

Não informado na issue original.