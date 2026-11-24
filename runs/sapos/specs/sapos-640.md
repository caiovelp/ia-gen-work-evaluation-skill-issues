# Spec: Quebra de tokens longos no corpo da simulação de notificação

## Objetivo

Na tela de simulação de notificação (`/notifications/:id/simulate`), um corpo de mensagem com uma URL longa, ou com qualquer sequência longa sem espaços, faz a tabela de resultados ficar mais larga que a janela. O efeito na página é este:

- a página inteira passa a rolar na horizontal;
- o cabeçalho e o menu, que ocupam 100% da viewport, terminam antes do conteúdo;
- o fundo da página aparece à direita.

**Causa identificada na issue:**

- A tabela em `app/views/notifications/simulate.html.erb:42` usa a classe `.notification-results`, que não tem nenhuma regra CSS no projeto.
- Com `table-layout: auto`, a largura mínima da célula "Corpo" é a largura do maior token indivisível do texto.
- A causa não está em `Notifier.body_whitespace_to_html` (`lib/notifier.rb:46`). Esse método mantém um espaço real em cada sequência de espaços (`lib/notifier.rb:52`), e esse comportamento está fixado em `spec/lib/notifier_spec.rb:316`.

**O que queremos:** a tabela de resultados fica dentro da largura disponível. Tokens longos no corpo quebram dentro da célula, de modo que o preview pode ser lido de relance sem rolagem horizontal.

**Usuário:** quem usa a tela de simulação para conferir o conteúdo de uma notificação antes do envio.

**Abordagem indicada pela issue:**

- Aplicar `table-layout: fixed` e `width: 100%` na tabela.
- Aplicar `overflow-wrap: anywhere` nas células. O valor `anywhere` é o ponto essencial: ao contrário de `word-break: break-word`, ele reduz a largura mínima de conteúdo, que é a métrica que faz a tabela estourar.

**Alternativa descartada pela issue:** envolver a tabela em `div.scrollable-table`, o padrão das telas de admissão em `app/assets/stylesheets/custom/tables.scss`. Isso só confina a rolagem à tabela, e um preview com rolagem horizontal é pior que uma URL partida.

**Não é regressão:**

- A tabela existe desde `aed6016e`.
- O preview do corpo existe desde `73667dea` (#530).
- O problema reproduz igual nas versões 7.15.21 e 7.15.22.

## Premissas

1. A aplicação é Rails, com views ERB, folhas de estilo SCSS em `app/assets/stylesheets/` e testes RSpec em `spec/`. Isso foi inferido dos caminhos citados na issue.
2. "Spec de feature (`js: true`)" indica Capybara com um driver que executa JavaScript. O driver exato não está informado.
3. A correção fica só em CSS (e, se necessário, em atributos de classe na view). `Notifier` e o HTML gerado para o corpo não mudam.
4. A classe `.notification-results` é usada apenas nessa tabela. A issue diz que ela não tem regras CSS, mas não diz se aparece em outras views.
5. Os navegadores-alvo suportam `overflow-wrap: anywhere`.
6. Quebrar visualmente a URL no meio é aceitável. A issue considera isso preferível à rolagem.

## Stack Tecnológica

Ruby on Rails (ERB), SCSS e RSpec, todos inferidos dos caminhos citados. As versões não foram informadas na issue original.

## Comandos

Não informado na issue original.

- Build: desconhecido
- Testes: desconhecido (presumivelmente RSpec, mas o comando exato não foi informado)
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Apenas os caminhos citados na issue:

```
app/views/notifications/simulate.html.erb   → View da simulação; tabela de resultados na linha 42
app/assets/stylesheets/custom/tables.scss   → Estilos de tabela existentes (ex.: .scrollable-table)
lib/notifier.rb                              → Notifier.body_whitespace_to_html (linhas 46 e 52)
spec/lib/notifier_spec.rb                    → Spec do Notifier; preservação de espaço real fixada na linha 316
```

Também não foram informados:

- o local da nova regra CSS (o próprio `tables.scss` ou outro arquivo);
- o diretório das specs de feature.

## Estilo de Código

Não informado na issue original.

## Estratégia de Testes

- **Nível:** spec de feature com `js: true`, porque o problema é de layout renderizado e só aparece num navegador real.
- **Cenário:**
  1. Fixar o tamanho da janela.
  2. Simular uma notificação cujo corpo contenha um token longo sem espaços, como uma URL longa.
  3. Comparar `document.documentElement.scrollWidth` com `clientWidth`.
- **Resultado esperado:** a spec falha antes da correção (`scrollWidth > clientWidth`) e passa depois (`scrollWidth <= clientWidth`).
- **Regressão existente:** `spec/lib/notifier_spec.rb` continua passando, incluindo o caso da linha 316.
- **Localização, nome do arquivo e driver:** não informados.
- **Meta de cobertura:** não informada.

## Limites

- **Sempre:**
  - Manter a correção restrita à apresentação da tabela de resultados da simulação.
  - Rodar a spec de feature nova e a `spec/lib/notifier_spec.rb` antes de considerar a tarefa concluída.
- **Perguntar antes:**
  - Alterar regras globais de tabela ou o padrão `.scrollable-table` existente.
  - Adicionar dependências ou drivers de teste.
  - Mudar larguras de colunas de forma que afete a legibilidade das outras colunas.
- **Nunca:**
  - Alterar `Notifier.body_whitespace_to_html` ou o comportamento fixado em `spec/lib/notifier_spec.rb:316`.
  - Truncar ou modificar o conteúdo do corpo exibido.
  - Resolver com rolagem confinada (`div.scrollable-table`), alternativa já descartada.

## Critérios de Sucesso

1. Com a janela em tamanho fixo, ao simular uma notificação cujo corpo tenha um token longo sem espaços, `document.documentElement.scrollWidth <= clientWidth`. A página não rola na horizontal.
2. A tabela `.notification-results` ocupa no máximo 100% da largura disponível do contêiner.
3. O token longo quebra dentro da célula "Corpo" e aparece por inteiro, distribuído em várias linhas, sem corte nem ocultação.
4. Cabeçalho e menu cobrem toda a largura visível da página, sem fundo exposto à direita.
5. Corpos com prosa comum continuam quebrando nos espaços como antes, e a formatação preservada pelo `Notifier` não muda.
6. `spec/lib/notifier_spec.rb` continua passando sem alterações.
7. A nova spec de feature falha sem a correção e passa com ela.

## Questões em Aberto

1. Em que arquivo a regra de `.notification-results` deve ficar: em `app/assets/stylesheets/custom/tables.scss` ou num stylesheet específico de notificações?
2. A classe `.notification-results`, ou essa tabela, é usada em alguma outra view que também seria afetada?
3. Com `table-layout: fixed`, as larguras das colunas passam a vir da primeira linha ou da distribuição igual. É preciso definir larguras explícitas, por exemplo dar mais espaço à coluna "Corpo"? Quais são as colunas da tabela?
4. `overflow-wrap: anywhere` deve valer para todas as células, como sugere a issue, ou só para a célula "Corpo"?
5. Quais navegadores precisam ser suportados? É preciso confirmar o suporte a `overflow-wrap: anywhere`.
6. Qual tamanho de janela a spec de feature deve fixar? A correção também deve ser verificada em larguras móveis?
7. Qual é o comando de execução dos testes, qual driver JS está configurado e onde ficam as specs de feature?
8. Além do corpo, outros campos exibidos na tabela (assunto, destinatário etc.) podem conter tokens longos e também precisam de cobertura?