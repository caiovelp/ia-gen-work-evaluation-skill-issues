# Especificação: Destaque visual do link de inscrição em disciplinas no painel do aluno

## Objetivo

O aviso com o link para inscrição em disciplinas, exibido no painel do aluno do SAPOS, usa o mesmo estilo visual do restante do painel. Por isso o aluno tem dificuldade para encontrar onde se inscrever.

O objetivo é dar a esse link a aparência de um botão ou elemento de chamada para ação, para que o aluno o identifique rapidamente.

**Usuário:** aluno autenticado que acessa o seu painel, especialmente durante um período de inscrição aberto.

**Histórias de usuário:**
- Como aluno, ao abrir meu painel durante um período de inscrição, quero ver imediatamente onde clicar para me inscrever em disciplinas, sem precisar procurar entre os demais itens.

**Critérios de aceitação (propostos):**
- O link de inscrição em disciplina aparece com estilo de botão ou de destaque, diferente dos demais itens do painel. O estilo deve seguir a referência da segunda imagem da issue.
- O destino e o comportamento do link continuam os mesmos.
- As condições de exibição do aviso e do link continuam as mesmas (por exemplo, só aparecem quando há período de inscrição aberto).
- O destaque é legível e acessível: contraste adequado, texto descritivo, foco visível pelo teclado.
- O restante do painel não muda visualmente.

## Premissas

1. O SAPOS (gems-uff/sapos) é uma aplicação web Ruby on Rails. Isso vem de conhecimento prévio do projeto e não foi verificado no repositório.
2. A mudança é apenas de apresentação (view/CSS). Não há alteração de rotas, controllers, regras de negócio nem banco de dados.
3. O conteúdo das imagens anexadas não pôde ser visto. A imagem 1 mostra o estado atual e a imagem 2 é uma referência aproximada ("algo mais ou menos assim"), não um design fechado.
4. O novo estilo deve reaproveitar classes ou componentes de estilo que o projeto já usa, sem adicionar dependências novas.
5. Se houver mais de um link ou aviso de inscrição (por exemplo, um por período ou turma), todos recebem o mesmo tratamento.
6. O mesmo destaque vale para telas desktop e móveis.

## Stack Tecnológica

Não informado na issue original. Supõe-se Ruby on Rails (ver Premissa 1). Versões, framework CSS e biblioteca de UI são desconhecidos.

## Comandos

Não informado na issue original.
- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Não informado na issue original. Não se sabe qual arquivo de view, partial ou folha de estilo renderiza o painel do aluno e o aviso de inscrição.

## Estilo de Código

Não informado na issue original. A mudança deve seguir as convenções de nomenclatura de classes CSS e a organização de views já existentes no projeto.

## Estratégia de Testes

Não informado na issue original. Sugestões, a confirmar:
- Verificação manual e visual do painel do aluno, com e sem período de inscrição aberto, comparando antes e depois.
- Se o projeto tiver testes de view ou de sistema/feature, adicionar ou ajustar um teste que confirme que o link de inscrição é renderizado com a classe ou elemento de destaque e mantém o mesmo destino.
- Verificação em pelo menos uma largura de tela móvel.

## Limites

- **Sempre:**
  - Manter destino, texto funcional e condições de exibição do link.
  - Reaproveitar estilos ou componentes já existentes no projeto.
  - Garantir contraste e foco acessíveis.
  - Rodar a suíte de testes existente antes de submeter.
- **Perguntar antes:**
  - Adicionar dependências de front-end (bibliotecas CSS/JS).
  - Alterar o texto do aviso.
  - Mudar a posição do aviso no painel.
  - Aplicar o novo estilo a outros links do painel.
  - Mexer em lógica de controller ou modelo.
- **Nunca:**
  - Alterar regras de negócio de inscrição.
  - Alterar o esquema do banco de dados.
  - Remover testes existentes.
  - Mudar o estilo global do painel para todos os itens.

## Critérios de Sucesso

- [ ] Em um ambiente com período de inscrição aberto, o link de inscrição aparece no painel do aluno com aparência de botão ou destaque, visualmente diferente dos demais itens.
- [ ] O visual é aprovado pelo autor da issue ou mantenedor como compatível com a referência (imagem 2).
- [ ] Clicar no link leva ao mesmo destino de antes da mudança.
- [ ] Sem período de inscrição aberto, o painel se comporta como antes (o aviso não aparece, ou aparece conforme a regra atual).
- [ ] Os demais elementos do painel não mudam visualmente.
- [ ] O elemento destacado tem contraste adequado (meta sugerida: WCAG AA) e foco visível via teclado.
- [ ] A suíte de testes existente passa.

## Perguntas em Aberto

1. Qual é exatamente o estilo desejado (cor, ícone, tamanho, botão ou caixa de alerta)? A imagem 2 é referência fechada ou só ilustrativa?
2. O texto do aviso ou link deve ser mantido igual ou pode ser reescrito para ficar mais claro (ex.: "Inscrever-se em disciplinas")?
3. O aviso deve mudar de posição no painel (por exemplo, ir para o topo) ou apenas mudar de estilo?
4. Pode haver mais de um link de inscrição ao mesmo tempo? Se sim, todos recebem o mesmo destaque?
5. Existe paleta de cores ou componente padrão de botão no SAPOS que deva ser usado?
6. Outros avisos do painel (ex.: pendências, prazos) devem ganhar destaque semelhante, ou apenas o de inscrição?
7. Há requisitos de responsividade ou de acessibilidade além do usual?
8. Quais arquivos (view/partial/CSS) renderizam esse aviso, e quais são os comandos de build e teste do projeto?