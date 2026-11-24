# Spec: Botões de formatação de texto nas declarações customizáveis

## Objetivo

Melhorar a usabilidade da funcionalidade de **declarações customizáveis**, adicionando ao editor de texto botões de formatação intuitivos. Hoje a edição não oferece ferramentas fáceis de formatação, o que dificulta o uso por pessoas sem conhecimentos técnicos avançados. A necessidade foi identificada na coleta de feedback dos usuários.

**Usuário:** pessoas que criam ou editam declarações customizáveis, incluindo quem não tem conhecimento técnico (por exemplo, quem não conhece HTML ou Markdown).

**Escopo mínimo citado na issue:**
- Negrito
- Itálico
- Alinhamento centralizado
- Alinhamento justificado

A issue usa "como", o que indica que a lista pode não ser exaustiva (ver Perguntas em Aberto).

**Histórias de usuário:**
- Como usuário sem conhecimento técnico, quero selecionar um trecho e clicar em um botão para deixá-lo em negrito ou itálico, sem precisar escrever marcação manual.
- Como usuário, quero centralizar ou justificar um parágrafo da declaração com um clique.
- Como usuário, quero que a formatação aplicada no editor apareça na declaração final gerada.

## Premissas

1. "Declarações customizáveis" é uma funcionalidade que já existe no sistema e já tem um campo de edição de texto. A issue fala em "atualmente, a edição de texto".
2. Hoje a formatação, se existir, depende de marcação manual (HTML, Markdown ou similar). A issue não confirma isso.
3. A melhoria é na interface web do editor, não em uma API ou aplicativo mobile.
4. A formatação aplicada no editor deve se manter ao salvar e aparecer na declaração gerada (visualização, impressão e/ou PDF).
5. Declarações já existentes devem continuar funcionando e sendo exibidas como antes.
6. Os botões seguem o padrão visual de barra de ferramentas comum em editores de texto (ícones reconhecíveis com dica de texto/tooltip).
7. O texto da declaração pode conter variáveis ou marcadores dinâmicos, e a formatação não pode quebrá-los. Isso é uma suposição a confirmar.

## Stack Tecnológica

Não informado na issue original. Linguagem, framework de frontend, componente de editor atual (textarea, editor rich text, etc.) e versões são desconhecidos.

## Comandos

Não informado na issue original.

```
Build: desconhecido
Test: desconhecido
Lint: desconhecido
Dev: desconhecido
```

## Estrutura do Projeto

Não informado na issue original. Não se sabe onde ficam o componente de edição das declarações, o modelo de dados das declarações ou a renderização final (ex.: geração de PDF).

## Estilo de Código

Não informado na issue original. Deve seguir as convenções já usadas no repositório, que não estão visíveis.

## Estratégia de Testes

Não informado na issue original. Como orientação, sem comandos ou caminhos definidos:
- **Unitários:** cada botão aplica e remove a formatação correspondente no trecho ou parágrafo selecionado.
- **Integração:** o conteúdo formatado é salvo e recarregado sem perda de formatação.
- **Renderização:** a declaração gerada (visualização/impressão/PDF, conforme existir) reflete negrito, itálico, centralizado e justificado.
- **Regressão:** declarações criadas antes da mudança continuam abrindo e sendo exibidas corretamente.
- **Segurança:** o conteúdo formatado é sanitizado, sem execução de scripts injetados, caso o formato armazenado seja HTML.
- **Usabilidade/acessibilidade (manual):** os botões têm rótulo ou tooltip, funcionam por teclado e indicam o estado ativo.

Framework de testes e metas de cobertura: desconhecidos.

## Limites

- **Sempre:**
  - Preservar o conteúdo e a exibição das declarações já existentes.
  - Sanitizar o conteúdo formatado antes de salvar e de renderizar.
  - Manter intactas as variáveis/marcadores dinâmicos das declarações, se existirem.
  - Rodar a suíte de testes existente antes de commitar.
- **Perguntar antes:**
  - Adicionar uma nova dependência, como uma biblioteca de editor rich text.
  - Alterar o formato de armazenamento do texto das declarações (ex.: texto puro → HTML) ou o schema do banco de dados.
  - Migrar dados de declarações existentes.
  - Alterar o mecanismo de geração do documento final (PDF/impressão).
  - Adicionar opções de formatação além das quatro citadas.
- **Nunca:**
  - Remover ou quebrar a edição por marcação manual, caso usuários avançados dependam dela, sem aprovação.
  - Salvar HTML não sanitizado.
  - Remover testes que estejam falhando sem aprovação.

## Critérios de Sucesso

1. O editor de declarações customizáveis exibe uma barra com botões de **negrito**, **itálico**, **centralizar** e **justificar**.
2. Ao selecionar um trecho e clicar em negrito ou itálico, a formatação é aplicada. Clicar de novo remove a formatação (comportamento de alternância).
3. Ao posicionar o cursor ou selecionar um parágrafo e clicar em centralizar ou justificar, o alinhamento do parágrafo muda.
4. Os botões indicam visualmente quando a formatação está ativa no trecho selecionado.
5. Cada botão tem tooltip/rótulo acessível em português e pode ser acionado por teclado.
6. A formatação persiste após salvar e recarregar a declaração.
7. A declaração gerada para o usuário final reflete fielmente a formatação aplicada no editor.
8. Declarações criadas antes da mudança abrem e são exibidas sem alteração.
9. Variáveis/marcadores dinâmicos continuam sendo substituídos corretamente em textos formatados, se aplicável.
10. Um usuário sem conhecimento técnico consegue aplicar as quatro formatações sem digitar nenhuma marcação. A forma de validar isso precisa ser definida (ver Perguntas em Aberto).

## Perguntas em Aberto

1. Como o editor de declarações funciona hoje: é um textarea simples, aceita HTML/Markdown manual ou já usa algum editor rich text?
2. Em que formato o texto das declarações é armazenado hoje, e em que formato deve ser armazenado após a mudança?
3. A lista (negrito, itálico, centralizado, justificado) é exaustiva? Devem entrar também sublinhado, alinhamento à esquerda/direita, listas, tamanho de fonte, desfazer/refazer etc.?
4. Pode-se adotar uma biblioteca de editor rich text pronta, ou a solução deve ser implementada sem novas dependências?
5. Onde a declaração final é exibida (tela, impressão, PDF)? Esse pipeline já suporta negrito, itálico e alinhamento?
6. As declarações usam variáveis/marcadores dinâmicos (ex.: nome, data)? Como devem se comportar quando formatados?
7. Os usuários avançados devem continuar podendo editar a marcação diretamente (ex.: um modo "código-fonte")?
8. Há atalhos de teclado esperados (ex.: Ctrl+B, Ctrl+I)?
9. Existem requisitos de acessibilidade ou de navegadores suportados?
10. Como será validado o critério de "intuitivo": nova rodada de feedback, teste com usuários ou apenas a presença dos botões?
11. Há outros pontos do feedback dos usuários sobre declarações customizáveis que devam entrar nesta entrega?