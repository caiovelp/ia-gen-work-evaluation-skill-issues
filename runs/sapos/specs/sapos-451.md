# Spec: Ordenação alfabética com acentos no quadro de horários

## Objetivo

Corrigir a ordenação alfabética das disciplinas no quadro de horários para que letras acentuadas não alterem a posição de um nome na ordem.

**Problema relatado:** nomes que começam com letra acentuada (ex.: _Álgebra Linear_, começando com _Á_) aparecem no final do quadro. Deveriam aparecer junto dos nomes que começam com a mesma letra sem acento (ex.: _Análise de Imagens_, começando com _A_). Esse comportamento é típico de uma comparação por ponto de código (Unicode/ASCII), em vez de uma comparação sensível ao idioma (locale/collation). Isso é uma hipótese: a causa não foi confirmada.

**Usuário:** quem consulta o quadro de horários e espera encontrar as disciplinas em ordem alfabética, conforme as convenções do português.

**Critérios de aceitação (histórias):**
- Como usuário, quero que _Álgebra Linear_ apareça entre as disciplinas iniciadas por "A", e não no final do quadro.
- Como usuário, quero que acentos e cedilha (á, à, â, ã, é, ê, í, ó, ô, õ, ú, ç etc.) não desloquem uma disciplina para fora de sua posição alfabética natural.

## Premissas

1. A ordem esperada segue as convenções do português (pt-BR): letras acentuadas são tratadas como equivalentes à letra base no nível primário de comparação. Ex.: "Á" ≈ "A" e "Ç" ≈ "C".
2. O problema afeta qualquer posição do nome, e não apenas a primeira letra. Ex.: "Cálculo" vs. "Calculo II".
3. A ordenação também deveria ignorar diferenças de maiúsculas/minúsculas no nível primário. A issue não menciona isso, mas é uma suposição razoável.
4. A ordenação acontece no código que monta o quadro de horários. Não se sabe se isso ocorre no frontend, no backend ou no banco de dados.
5. Os nomes exibidos no quadro são os mesmos usados como chave de ordenação.
6. Nenhuma outra tela ou lista está no escopo. Porém, se houver uma função de ordenação compartilhada, outras listas podem ser afetadas.

## Stack Tecnológica

Não informado na issue original. Linguagem, framework e dependências são desconhecidos.

## Comandos

Não informado na issue original.

```
Build: desconhecido
Test: desconhecido
Lint: desconhecido
Dev: desconhecido
```

## Estrutura do Projeto

Não informado na issue original. A localização do código que gera e ordena o quadro de horários é desconhecida.

## Estilo de Código

Não informado na issue original. Deve-se seguir as convenções já existentes no repositório.

## Estratégia de Testes

O framework e o local dos testes não foram informados na issue original. Expectativas independentes da stack:

- **Teste unitário** da função ou comparador de ordenação, com casos que incluam:
  - `["Análise de Imagens", "Álgebra Linear", "Banco de Dados"]` → `["Álgebra Linear", "Análise de Imagens", "Banco de Dados"]`
  - Acentos em posições não iniciais (ex.: "Cálculo I", "Calculo Numérico").
  - Cedilha (ex.: "Computação" vs. "Comunicação").
  - Maiúsculas e minúsculas misturadas, caso a premissa 3 seja confirmada.
  - Nomes que diferem apenas pelo acento: a ordem deve ser determinística e estável.
- **Teste de integração ou de interface** (se existir infraestrutura para isso): o quadro de horários renderizado exibe as disciplinas na ordem esperada.
- Antes da correção, um teste de regressão deve reproduzir o bug, ou seja, falhar com a implementação atual.

## Limites

- **Sempre:** reproduzir o bug com um teste antes de corrigir; manter a ordenação determinística; rodar a suíte de testes existente antes de submeter; manter os nomes exibidos exatamente como estão (sem remover acentos na exibição).
- **Perguntar antes:** adicionar dependências (ex.: bibliotecas de collation/ICU); alterar o collation ou o esquema do banco de dados; mudar uma função de ordenação compartilhada que afete outras telas; alterar a forma como os nomes das disciplinas são armazenados.
- **Nunca:** alterar ou normalizar permanentemente os dados das disciplinas para remover acentos; remover ou desativar testes existentes sem aprovação.

## Critérios de Sucesso

- No quadro de horários, _Álgebra Linear_ aparece antes de _Análise de Imagens_ e entre as disciplinas iniciadas por "A". Pelas regras de collation pt-BR, "Ál**g**" < "An" no nível primário.
- Nenhuma disciplina cujo nome começa com letra acentuada aparece deslocada para o final do quadro.
- Acentos e cedilha em qualquer posição do nome não alteram a ordem no nível primário. Eles servem apenas como critério de desempate.
- Os nomes continuam sendo exibidos com seus acentos originais.
- Testes automatizados cobrindo os casos acima passam, e a suíte existente continua passando.

## Questões em Aberto

1. Onde a ordenação é feita hoje: frontend, backend ou consulta ao banco (ex.: `ORDER BY`)? Qual linguagem e framework são usados?
2. Qual locale deve ser usado como referência: pt-BR, ou o locale do usuário ou do navegador?
3. A ordenação deve ignorar maiúsculas/minúsculas?
4. Quando dois nomes diferem apenas pelo acento, qual deve vir primeiro (ex.: sem acento antes de com acento)?
5. Existem outras listas no sistema (ex.: lista de disciplinas, professores, salas) com o mesmo problema que devam entrar no escopo?
6. O ambiente de execução tem suporte a collation por locale (ex.: dados ICU disponíveis no runtime ou no banco)? Isso pode influenciar a abordagem e a necessidade de dependências.
7. Quais são os comandos de build, teste e lint, e onde ficam os testes no repositório?