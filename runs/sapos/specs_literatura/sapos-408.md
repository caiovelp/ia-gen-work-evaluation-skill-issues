## Resumo
Criar no SAPOS o conceito de Linhas de Pesquisa, vinculadas a Áreas de Pesquisa.

## Descrição
É necessário criar no SAPOS um novo modelo para registrar linhas de pesquisa. Cada linha de pesquisa pertence a uma área de pesquisa. Ao cadastrar uma linha, o usuário deve indicar a qual área ela pertence.

A relação proposta é de todo e parte, como a que já existe entre País e Estado. A Área de Pesquisa é o todo e a Linha de Pesquisa é a parte.

Hoje o SAPOS tem apenas o campo "área de pesquisa". O conceito "área de pesquisa" não pode ser reaproveitado para registrar a linha, porque é usado no histórico, no campo "área de concentração". Por isso é preciso um conceito novo.

## Versão do produto
Não informado na issue original.

## Justificativa
Antes, o programa tinha 7 áreas de pesquisa, e o campo "área de pesquisa" atendia bem. Agora o programa tem apenas uma área (Ciência da Computação), e as 7 áreas antigas passaram a ser linhas de pesquisa. O programa quer registrar a linha de pesquisa de cada aluno, e o modelo atual não permite isso.

## Caso de uso ou cenário
Sugestão do professor Leonardo Murta:

1. O usuário cadastra as linhas de pesquisa (as 7 áreas antigas) e associa cada uma à área "Ciência da Computação".
2. Na matrícula de um aluno, o usuário registra a linha de pesquisa do aluno, além da área de concentração.
3. A área de concentração continua sendo usada no histórico do aluno.

## Solução possível
A issue sugere:

- **Modelagem:** criar uma entidade "Linha de Pesquisa" que pertence a uma "Área de Pesquisa", no mesmo padrão de País/Estado.
- **Matrícula, opção 1:** indicar somente a linha de pesquisa e inferir a área a partir dela.
- **Matrícula, opção 2 (facilita a migração):** manter o campo "área de concentração" e adicionar o campo "linha de pesquisa". Esse campo deve mostrar apenas as linhas cadastradas para a área selecionada.