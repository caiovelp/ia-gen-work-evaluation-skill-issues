## Resumo

Na tela de simulação de notificação (`/notifications/:id/simulate`), quando o corpo da mensagem contém uma URL longa ou qualquer sequência longa sem espaços, a tabela de resultados fica mais larga que a janela e a página inteira passa a rolar horizontalmente.

Análise do autor da issue:
- A tabela está em `app/views/notifications/simulate.html.erb:42` e não tem restrição de largura. A classe `.notification-results` não possui nenhuma regra CSS no projeto.
- Com `table-layout: auto`, a largura mínima da célula "Corpo" é a do maior token indivisível do texto. Uma URL longa não oferece ponto de quebra, então a tabela estica até caber.
- O problema não vem da conversão de espaços em `&nbsp;`. `Notifier.body_whitespace_to_html` (`lib/notifier.rb:46`) preserva a formatação, mas mantém um espaço real em cada sequência (`lib/notifier.rb:52`, comportamento fixado em `spec/lib/notifier_spec.rb:316`). Texto com espaços quebra normalmente. Só tokens sem espaço estouram o layout.

## Passos para reproduzir

1. Ter uma notificação cujo corpo contenha uma URL longa, ou qualquer sequência longa de caracteres sem espaços.
2. Acessar a tela de simulação dessa notificação (`/notifications/:id/simulate`) e simular a notificação.
3. Observar a largura da tabela de resultados e a rolagem da página.

## Comportamento observado

- A tabela de resultados cresce além da largura da janela.
- A página inteira passa a rolar horizontalmente.
- O cabeçalho e o menu, dimensionados a 100% da viewport, terminam antes do conteúdo, e o fundo da página fica exposto à direita.

## Comportamento esperado

A tabela de resultados deve caber na largura da janela, sem rolagem horizontal da página, mesmo com corpos que contenham URLs ou outros tokens longos sem espaços. Segundo o autor, o preview de e-mail existe para ser lido de relance, então o corpo deve ser legível sem rolagem horizontal.

## Stack trace / saída de erro

Não informado na issue original.

## Caso de teste

Teste proposto na issue (spec de feature com `js: true`):

1. Fixar o tamanho da janela do navegador.
2. Simular uma notificação cujo corpo contenha um token longo sem espaços.
3. Comparar `document.documentElement.scrollWidth` com `clientWidth`. Não deve haver rolagem horizontal, ou seja, `scrollWidth` não deve exceder `clientWidth`.

Segundo o autor, esse teste falha no comportamento atual e deve passar quando o problema for resolvido.

## Exemplo de código

Não informado na issue original.

## Versão e ambiente

- Reproduz igualmente nas versões 7.15.21 e 7.15.22.
- Não é regressão: a tabela existe desde o commit `aed6016e`, e o preview do corpo desde `73667dea` (#530).
- Navegador e sistema operacional: não informados na issue original.