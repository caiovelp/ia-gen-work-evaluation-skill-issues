## Resumo
A issue relata dois problemas no processo seletivo:

1. **Empate no ranking:** quando há empate na penúltima posição de algum grupo do ranking, a vaga não é descontada das vagas disponíveis para o grupo.
2. **Número mínimo de cartas:** quando o edital especifica um número mínimo de cartas, o sistema não valida se o edital tem um modelo de formulário de carta. Ao submeter uma inscrição, ocorre um erro.

## Passos para reproduzir
**Problema 1 – Empate na penúltima posição do ranking**
1. Ter um processo seletivo com ranking dividido em grupos, cada um com um número de vagas disponíveis.
2. Fazer com que dois ou mais candidatos fiquem empatados na penúltima posição de um grupo.
3. Gerar ou verificar o ranking e observar as vagas disponíveis do grupo.

**Problema 2 – Edital com número mínimo de cartas**
1. Criar ou configurar um edital que especifique um número mínimo de cartas.
2. Não associar ao edital um modelo de formulário de carta. O sistema não impede essa configuração.
3. Submeter uma inscrição nesse edital.

## Comportamento observado
- **Problema 1:** a vaga ocupada pelo empate na penúltima posição não é descontada das vagas disponíveis para o grupo.
- **Problema 2:** o sistema aceita o edital sem validar o modelo de formulário de carta. Ao submeter uma inscrição, ocorre um erro. A issue não descreve qual erro.

## Comportamento esperado
- **Problema 1:** a vaga ocupada na penúltima posição deve ser descontada das vagas disponíveis para o grupo, mesmo quando há empate.
- **Problema 2:** quando o edital especifica um número mínimo de cartas, o sistema deve validar o modelo de formulário de carta no edital. A submissão de uma inscrição não deve gerar erro.

## Stack trace / saída de erro
Não informado na issue original. A issue apenas diz que "dá erro" ao submeter uma inscrição (problema 2), sem mensagem nem stack trace.

## Caso de teste
Não informado na issue original.

## Exemplo de código
Não informado na issue original.

## Versão e ambiente
Não informado na issue original.