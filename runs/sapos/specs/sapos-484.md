# Spec: Redução de espaços vazios nas páginas do PDF de quadros de horários

## Premissas
1. O PDF de "quadro de horários" é gerado por funcionalidade já existente no sistema. Não há como ver na issue qual biblioteca ou mecanismo gera o PDF (por exemplo, HTML→PDF ou geração programática).
2. O documento contém vários blocos/quadros, como um quadro por turma, professor, sala ou curso. Hoje cada bloco, ou um grupo deles, pode forçar quebra de página.
3. O problema é de **paginação/layout**: blocos que caberiam no espaço restante da página vão para a página seguinte, ou há quebras explícitas desnecessárias.
4. O conteúdo do quadro (dados, horários, ordem) não deve mudar. Muda apenas a distribuição nas páginas.
5. Um único quadro não deve ser partido entre duas páginas se couber inteiro em uma página. A legibilidade de cada quadro prevalece sobre a economia de espaço.
6. O tamanho de papel e a orientação atuais (A4? retrato/paisagem?) continuam como estão.
7. Trata-se de uma única capacidade (layout do PDF), então a Fase 0 (mapa de capacidades) não se aplica.

## Objetivo
Melhorar o aproveitamento das páginas do PDF de quadros de horários. A meta é reduzir áreas em branco e o número total de páginas, sem prejudicar a legibilidade.

- **Usuário:** quem gera, imprime ou distribui os quadros de horários (por exemplo, coordenação ou secretaria; perfil exato não informado).
- **Problema atual:** o gerador inicia novas páginas mesmo quando há grande espaço vazio na página corrente.
- **Sucesso:** um quadro só começa em nova página quando não cabe no espaço restante da página atual, ou quando há uma regra explícita e justificada para isso.

**Critérios de aceitação (proposta):**
- Dado um PDF com vários quadros, quando o quadro seguinte cabe inteiro no espaço restante da página, ele é renderizado na mesma página.
- Um quadro que cabe em uma página nunca é dividido entre páginas.
- Um quadro maior que uma página é dividido de forma legível: cabeçalho da tabela repetido e linhas não cortadas ao meio.
- O número de páginas para um mesmo conjunto de dados é menor ou igual ao gerado hoje.
- Cabeçalhos, rodapés, títulos e conteúdo dos quadros permanecem corretos e completos.

## Stack Tecnológica
Não informado na issue original. A linguagem, o framework e a biblioteca de geração de PDF são desconhecidos.

## Comandos
Não informado na issue original.
- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Execução/geração do PDF: desconhecido

## Estrutura do Projeto
Não informado na issue original. A localização do código de geração do PDF e dos templates é desconhecida.

## Estilo de Código
Não informado na issue original. Seguir as convenções já existentes no módulo de geração de PDF.

## Estratégia de Testes
Framework e local dos testes: não informados na issue original. Abordagem proposta:
- **Testes automatizados (se viáveis):** gerar o PDF a partir de dados fixos e verificar:
  - número de páginas, comparado com um valor de referência ou com o comportamento anterior;
  - ausência de quadros partidos quando cabem em uma página.
- **Casos de teste com dados variados:**
  - um único quadro pequeno;
  - muitos quadros pequenos;
  - quadros de alturas diferentes;
  - um quadro maior que uma página;
  - quadro com muitas linhas ou textos longos nas células.
- **Verificação visual manual:** comparar o PDF antes e depois em casos representativos, de preferência com um exemplo real que exiba o problema.

## Limites
- **Sempre:** preservar todo o conteúdo e a ordem dos quadros; manter a legibilidade; testar com conjuntos de dados de tamanhos variados.
- **Perguntar antes:**
  - mudar tamanho de papel, orientação, margens ou fontes;
  - reordenar quadros para "encaixar" melhor;
  - trocar ou adicionar biblioteca de geração de PDF;
  - remover quebras de página que possam ser intencionais (por exemplo, um quadro por página para afixação).
- **Nunca:**
  - cortar ou omitir conteúdo;
  - dividir uma linha da tabela entre páginas;
  - reduzir a fonte a ponto de prejudicar a leitura sem aprovação.

## Critérios de Sucesso
- Para um conjunto de dados de referência que hoje exibe o problema, o novo PDF tem menos páginas, ou no máximo o mesmo número, e nenhuma página termina com espaço vazio suficiente para o quadro seguinte.
- Nenhum quadro que caiba em uma página aparece dividido.
- Quadros maiores que uma página mantêm o cabeçalho repetido e as linhas íntegras.
- Nenhuma regressão no conteúdo: mesmos quadros, dados e ordem.
- O tempo de geração do PDF não piora de forma perceptível (limite exato a definir).

## Questões em Aberto
1. Qual biblioteca ou mecanismo gera o PDF hoje? Onde fica o código e o template?
2. Existe um exemplo concreto (dados ou PDF) que reproduza o problema? Qual o tamanho típico dos quadros e quantos aparecem por arquivo?
3. As quebras de página atuais são explícitas (por exemplo, uma quebra fixa a cada quadro ou a cada N quadros)? Há algum motivo de negócio para elas, como imprimir um quadro por folha para afixar?
4. Pode haver mais de um quadro por página? E, se sim, lado a lado ou apenas empilhados?
5. É aceitável dividir um quadro entre páginas? Se sim, em que condições?
6. A ordem dos quadros pode ser alterada para otimizar o encaixe, ou deve ser preservada?
7. Podemos ajustar margens, espaçamento entre quadros, tamanho de fonte ou orientação da página?
8. O problema ocorre em todos os tipos de quadro de horários (por turma, professor, sala…) ou em algum específico?
9. Há uma meta quantitativa, como uma redução de X% no número de páginas ou um máximo de espaço vazio por página?
10. A mudança deve ser o novo padrão para todos, ou uma opção configurável na geração?