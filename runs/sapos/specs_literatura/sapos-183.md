## Resumo
Verificar o credenciamento dos orientadores ao salvar uma matrícula.

## Descrição
Ao salvar uma matrícula, o sistema deve verificar se pelo menos um dos orientadores do aluno é credenciado no nível da matrícula.

Regras:
- A matrícula deve ter **pelo menos um** orientador credenciado no nível da matrícula do aluno.
- É permitido haver orientadores não credenciados nesse nível.
- Um orientador não credenciado no nível da matrícula **não pode** ser o orientador principal.

## Versão do produto
Não informado na issue original.

## Justificativa
Não informado na issue original.

## Caso de uso ou cenário
Um aluno tem matrícula de nível mestrado. Ao salvar a matrícula, o sistema verifica se ele tem pelo menos um orientador credenciado no nível mestrado. Outros orientadores sem credenciamento no mestrado podem constar na matrícula, desde que nenhum deles seja o orientador principal.

## Solução possível
A issue sugere fazer a checagem no momento em que a matrícula é salva. A validação deve exigir pelo menos um orientador credenciado no nível da matrícula e impedir que um orientador não credenciado nesse nível seja o orientador principal.