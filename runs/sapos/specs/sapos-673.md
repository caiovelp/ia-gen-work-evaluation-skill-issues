# Spec: Centralizar a marca d'água no papel (`pdf_helper`)

## Premissas

1. A geração de PDF usa **Prawn**, ou uma biblioteca com a mesma API. A issue cita `pdf.stamp_at`, `at: [0, 0]` e rotação em torno da origem, mas não nomeia a biblioteca nem a versão.
2. "Centralizada" significa que o **centro da caixa da tinta** da marca, já rotacionada, coincide com o **centro do papel**. O centro da área útil entre margens não serve, porque a issue pede independência da margem inferior.
3. O **ângulo de rotação**, a **fonte** (monoespaçada), o **tamanho**, a **cor** e a **opacidade** atuais continuam iguais. Só a posição muda.
4. O texto continua vindo de `pdf_content.watermark`, presumivelmente uma chave de i18n. O conteúdo não é alterado.
5. Boletim, histórico e declaração usam todos o helper em `app/helpers/pdf_helper.rb`. A correção no helper vale para os três, sem mudanças por documento.
6. A marca continua sendo aplicada por *stamp* em todas as páginas, como hoje.
7. "Faixa da marca" é a região derivada das dimensões do papel onde o texto é centralizado. Pode ser, por exemplo, a diagonal ou o eixo rotacionado que passa pelo centro da página.

## Objetivo

A marca d'água dos documentos em PDF (boletim, histórico, declaração) é carimbada hoje numa coordenada fixa (`pdf.stamp_at "watermark", [80, 0]`). O texto é desenhado em `at: [0, 0]` dentro de uma rotação em torno da origem. Como nada mede a frase nem o papel, a marca não fica centralizada por construção. No A4 retrato, a tinta fica cerca de 35 pt à esquerda e cerca de 92 pt abaixo do centro da página.

Isso tem três efeitos, todos medidos:

1. A posição varia com a **margem inferior**, que cresce para caber o rodapé de assinatura. A diferença é de 69,65 pt entre um documento sem assinatura e um com assinatura manual.
2. A posição varia com o **comprimento da frase**. A fonte é monoespaçada, então editar ou traduzir `pdf_content.watermark` desloca a marca inteira.
3. Em papel **paisagem**, a borda corta a tinta. Nenhum documento com marca d'água usa paisagem hoje.

**O que construir:** calcular a faixa da marca a partir das dimensões do próprio papel e centralizar nela o texto medido. A marca deve ficar centrada na página independentemente da margem, do texto e da orientação.

**Usuários afetados:** quem emite e quem recebe os documentos com marca d'água.

**Origem:** issue #121.

## Stack Tecnológica

- Ruby, possivelmente Rails, dado o caminho `app/helpers/`. A versão não foi informada na issue original.
- Biblioteca de PDF: presumivelmente Prawn (ver Premissa 1). A versão não foi informada na issue original.

## Comandos

- Build: Não informado na issue original.
- Testes: Não informado na issue original.
- Lint: Não informado na issue original.
- Dev: Não informado na issue original.

## Estrutura do Projeto

- `app/helpers/pdf_helper.rb`: helper compartilhado que desenha e carimba a marca d'água. É o ponto da correção.
- `pdf_content.watermark`: chave do texto da marca. O arquivo onde ela está definida não foi informado na issue original.
- Geradores e templates de boletim, histórico e declaração: os caminhos não foram informados na issue original.
- Diretório de testes: não informado na issue original.

## Estilo de Código

Não informado na issue original. Seguir as convenções já presentes em `app/helpers/pdf_helper.rb`.

## Estratégia de Testes

- O framework de testes não foi informado na issue original.
- O teste deve gerar o PDF e **medir a caixa delimitadora da tinta** da marca, comparando seu centro com o centro da página, sem depender de coordenadas fixas. A ferramenta de inspeção de PDF disponível não foi informada na issue original.
- A variação deve ser coberta por estas combinações:
  - margem inferior: sem assinatura e com assinatura manual;
  - comprimento da frase: o texto atual, um texto mais curto e um mais longo;
  - orientação: A4 retrato e A4 paisagem;
  - tipo de documento: boletim, histórico e declaração, pelo menos um teste de fumaça de cada.
- Os testes existentes de PDF, se houver, devem continuar passando. Nenhum teste deve ser removido.

## Limites

- **Sempre:**
  - calcular a posição a partir do tamanho do papel e da largura medida do texto, sem constantes mágicas de posição;
  - manter a correção dentro do helper compartilhado;
  - rodar os testes antes de submeter.
- **Perguntar antes:**
  - mudar ângulo, fonte, tamanho, cor ou opacidade da marca;
  - reduzir a fonte automaticamente quando a frase não couber;
  - alterar o texto de `pdf_content.watermark`;
  - adicionar dependências, por exemplo para inspecionar PDFs nos testes.
- **Nunca:**
  - ajustar a coordenada fixa "no olho" para o caso A4 retrato atual;
  - fazer a posição da marca depender das margens ou do rodapé de assinatura;
  - alterar o layout do conteúdo ou do rodapé dos documentos.

## Critérios de Sucesso

1. **A4 retrato:** o centro da caixa da tinta da marca coincide com o centro da página dentro de uma tolerância T. Hoje o desvio é de cerca de 35 pt na horizontal e 92 pt na vertical. O valor de T está em aberto (ver Questões em Aberto).
2. **Independência da margem:** a posição da marca é a mesma, dentro de T, num documento sem assinatura e num com assinatura manual. Hoje a diferença é de 69,65 pt.
3. **Independência do texto:** para frases de comprimentos diferentes, o centro da tinta continua no centro da página dentro de T.
4. **Paisagem:** em A4 paisagem, a tinta fica centralizada dentro de T e **nenhuma parte é cortada** pela borda do papel, pelo menos para o texto atual.
5. **Abrangência:** os critérios 1 a 3 valem para boletim, histórico e declaração.
6. **Aparência preservada:** ângulo, fonte, tamanho, cor e opacidade da marca são os mesmos de antes.
7. Nenhum outro elemento dos PDFs muda de posição.

## Questões em Aberto

1. Qual tolerância T define "centralizado"? Por exemplo, ≤ 1 pt.
2. O que fazer quando a frase rotacionada não cabe no papel (texto longo ou traduzido, ou paisagem)? As opções são reduzir a fonte até caber, quebrar em linhas ou aceitar o corte.
3. O ângulo de rotação deve continuar fixo, ou deve acompanhar a diagonal do papel, que é diferente em retrato e em paisagem?
4. Confirmar que "centro" significa o centro do papel, e não o centro da área de conteúdo entre margens.
5. A centralização deve usar a caixa visual da tinta (glifos, incluindo ascendentes e descendentes) ou a caixa tipográfica (largura × altura da linha)? Isso afeta o resultado em alguns pontos.
6. Quais são a biblioteca de PDF e a versão, e quais são os comandos de teste e lint do projeto?
7. Já existe infraestrutura de teste que inspecione o conteúdo dos PDFs gerados, como a medição citada na issue? Se existe, onde está?
8. Há outros tamanhos de papel além de A4 que precisam ser suportados (por exemplo, Carta/Letter ou Ofício)?