# Especificação: Testes de caracterização (golden-master) para saídas PDF/XLSX

## Objetivo

Criar uma rede de proteção contra regressões na geração de PDF (prawn) e XLSX (caxlsx) durante upgrades de dependências e, principalmente, antes do salto para o Rails 8. O teste deve indicar se a saída **continua igual** ao baseline capturado. Ele não precisa afirmar que a saída está *correta*.

**Situação atual:**
- Os feature specs baixam o arquivo e conferem apenas o **nome**.
- Nenhum teste verifica conteúdo ou layout.
- A fidelidade só é checada na homologação, que é manual.

**Usuários:** desenvolvedores que fazem refatorações e upgrades e que precisam de sinal automático quando uma saída gerada muda.

**Histórias de usuário:**
- Como dev, ao atualizar uma gem de renderização, quero que a suíte falhe se o conteúdo de um PDF ou XLSX mudar em relação ao baseline.
- Como dev, quero um único helper (`expect_matches_golden(file, generator)`) que escolha a normalização ou a leitura conforme a extensão do arquivo, sem lógica específica em cada spec.
- Como dev, quero que a comparação ignore variações não determinísticas, como datas, `/ID`, mtimes do zip e o QR de assinatura, para evitar falsos positivos.

**Escopo inicial:** as saídas que mais doem se saírem erradas, ou seja, boletim/relatório e o XLSX de admissão.

## Premissas

1. A suíte de testes usa RSpec, já que a issue menciona "request spec" e "feature specs".
2. Os feature specs atuais dependem de chromedriver (Capybara/Selenium ou similar). Os novos testes **não** devem depender dele.
3. A aplicação está hoje em uma versão do Rails anterior à 8. A versão exata não foi informada.
4. O PDF é gerado com `prawn` e o XLSX com `caxlsx`.
5. Os arquivos golden são versionados no repositório.
6. O QR de assinatura é a única fonte de não-determinismo do PDF que não se resolve congelando o relógio. O conteúdo textual fora do QR é determinístico depois que o relógio é congelado.
7. A abordagem 2 (semântica) é aceitável como ponto de partida, mesmo sem detectar mudanças puramente de layout. Ver Perguntas em Aberto.
8. Gerar a saída via request spec exercita o mesmo caminho de renderização usado em produção pelo controller. O caminho cron/rake (#632) **não** é coberto automaticamente por isso.

## Stack Tecnológica

- Ruby on Rails, em versão pré-8. A versão exata não foi informada.
- RSpec (premissa).
- `prawn` para geração de PDF.
- `caxlsx` para geração de XLSX.
- `pdf-reader` para leitura semântica de PDF. A issue propõe a gem, mas não informa se ela já é dependência.
- `roo` para leitura semântica de XLSX. A issue propõe a gem, mas não informa se ela já é dependência.
- As versões das gems não foram informadas.

## Comandos

Não informado na issue original.

- Build: desconhecido
- Testes: desconhecido (provavelmente `bundle exec rspec`, não confirmado)
- Lint: desconhecido
- Regravação do baseline golden: a definir (ver Perguntas em Aberto)

## Estrutura do Projeto

Não informado na issue original.

- Localização dos request specs: desconhecida
- Localização dos helpers de suporte de teste: desconhecida
- Localização dos arquivos golden: a definir
- Localização dos geradores de PDF/XLSX e dos caminhos cron/rake (#632): desconhecida

## Estilo de Código

Não informado na issue original.

A única interface citada é a assinatura proposta do helper:

```ruby
expect_matches_golden(file, generator)
```

A semântica exata do parâmetro `generator` não foi definida (ver Perguntas em Aberto).

## Estratégia de Testes

**Nível:** request spec. A escolha é intencional: é mais rápido e evita o acoplamento com chromedriver dos feature specs.

**Mecanismo, conforme o tipo de arquivo:**

| Tipo | Abordagem 1: normalizar e comparar bytes | Abordagem 2: comparação semântica |
|---|---|---|
| PDF | Congelar relógio; zerar `/CreationDate`, `/ModDate` e `/ID`; **mascarar a região do QR** nos PDFs assinados | `pdf-reader`: texto por página e número de páginas |
| XLSX | Congelar relógio; zerar os timestamps de `docProps/core.xml` e os mtimes das entradas do zip | `roo`: matriz de células por planilha |

**Trade-offs registrados na issue:**
- A abordagem 1 detecta layout, mas exige mascarar o QR, o que não é trivial.
- A abordagem 2 é imune a timestamp e QR, robusta e simples, mas não detecta mudanças puramente de layout.

**Fluxo de caracterização:**
1. Capturar a saída no código atual e gravá-la como baseline.
2. Gerar a saída no código novo.
3. Normalizar ou ler as duas e comparar.
4. Falhar com um diff legível em caso de divergência.

**Cobertura inicial:**
- Boletim/relatório (PDF, assinado com QR).
- XLSX de admissão.

A expectativa numérica de cobertura não foi informada.

## Limites

- **Sempre:**
  - Congelar o relógio ao gerar saídas comparadas.
  - Manter a comparação determinística: rodar duas vezes seguidas sobre o mesmo código deve sempre passar.
  - Versionar os arquivos golden junto ao código.
  - Escrever os testes em nível de request spec.
  - Despachar a normalização pela extensão do arquivo, dentro do helper único.
- **Perguntar antes:**
  - Adicionar `pdf-reader` ou `roo` ao Gemfile, se ainda não forem dependências.
  - Alterar o código de geração de PDF/XLSX ou a lógica do QR de assinatura para torná-lo determinístico em teste, por exemplo injetando o nonce.
  - Alterar a configuração de CI.
  - Converter ou remover os feature specs de *smoke* existentes.
- **Nunca:**
  - Regravar o baseline automaticamente quando o teste falha.
  - Usar feature spec com chromedriver para esses testes.
  - Desabilitar a assinatura ou o QR em produção para fazer o teste passar.
  - Commitar dados sensíveis reais (ex.: dados de alunos) nos arquivos golden.

## Critérios de Sucesso

- [ ] O helper `expect_matches_golden(file, generator)` existe e trata `.pdf` e `.xlsx` conforme a extensão.
- [ ] Uma extensão não suportada gera um erro explícito, não uma comparação silenciosa.
- [ ] Gerar a mesma saída duas vezes sobre o mesmo código, com o relógio congelado, passa no helper em 100% das execuções. Isso inclui o PDF assinado com QR.
- [ ] Uma alteração deliberada de conteúdo faz o teste falhar com mensagem que indica a divergência. Exemplos: mudar um texto do boletim ou o valor de uma célula do XLSX de admissão.
- [ ] Existem request specs golden para o boletim/relatório (PDF) e para o XLSX de admissão, sem dependência de chromedriver.
- [ ] Existe um procedimento documentado e explícito para regravar o baseline.
- [ ] Os baselines foram capturados na versão atual (pré-Rails 8) e estão versionados.
- [ ] Se for adotada a abordagem 1, ou uma abordagem híbrida, uma alteração deliberada de layout que preserve o texto faz o teste falhar. Exemplo: mudar uma margem.

## Perguntas em Aberto

1. **Qual abordagem adotar?** As opções são 1 (bytes normalizados), 2 (semântica) ou um híbrido, por exemplo semântica para PDFs assinados e bytes para os demais. Detectar mudança de layout é requisito, ou basta conteúdo?
2. **QR de assinatura:** devemos mascarar a região, ou é aceitável injetar nonce/assinatura determinísticos no ambiente de teste? A segunda opção exige mexer no código de geração.
3. **Parâmetro `generator`:** o que ele representa? Um identificador nomeando o golden, um bloco ou callable que gera o arquivo, ou o nome da classe geradora?
4. **Armazenamento do golden:** onde ficam os arquivos e em que formato? Podem ser o arquivo binário original ou uma representação já normalizada/extraída (texto, JSON de células), que dá diffs mais legíveis no PR.
5. **Regravação do baseline:** como regravar? Opções: variável de ambiente, rake task ou outra. Quem pode aprovar uma regravação?
6. **Dependências:** `pdf-reader` e `roo` já estão no Gemfile, mesmo que só no grupo de teste?
7. **#632 (caminho cron/rake):** a cobertura do caminho cron/rake, onde ocorreu o anexo de 0 byte, entra no escopo desta issue ou fica separada? Se entrar, em que nível de teste, já que não é request spec? O comentário referenciado em #632 não está disponível aqui.
8. **Fixtures/dados:** quais dados de teste alimentam as saídas? Já existem factories ou fixtures estáveis o suficiente para não mudar o golden por acaso, por exemplo IDs sequenciais ou ordenação não determinística?
9. **Escopo além do inicial:** existe uma lista completa de saídas PDF/XLSX a cobrir depois do boletim/relatório e do XLSX de admissão?
10. **Feature specs de smoke existentes:** devem ser mantidos, removidos ou convertidos depois que os golden tests existirem?
11. **Prazo:** qual é a data prevista do salto para o Rails 8, que define o limite para capturar os baselines?