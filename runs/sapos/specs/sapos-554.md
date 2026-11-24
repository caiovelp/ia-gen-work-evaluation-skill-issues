# Spec: Correção do erro ao visualizar bolsa com alocação sem data limite de concessão

## Objetivo

Na tela de bolsas, o ícone de visualização ("olhinho") gera um erro em algumas bolsas: aquelas que possuem pelo menos uma alocação sem a **data limite de concessão** preenchida.

O objetivo é que o usuário consiga visualizar os detalhes de **qualquer** bolsa sem erro, inclusive quando alguma alocação não tem data limite de concessão.

**Usuário:** quem acessa a tela de bolsas e consulta os detalhes de uma bolsa. O perfil exato não foi informado na issue original.

**Critérios de aceitação (história de usuário):**
- Como usuário da tela de bolsas, ao clicar no "olhinho" de uma bolsa que tem alocação sem data limite de concessão, quero ver os detalhes da bolsa normalmente, sem erro.
- O campo de data limite de concessão vazio deve ser exibido de forma clara (ver Questões em Aberto), sem quebrar a tela.

## Premissas

1. O erro ocorre ao abrir a visualização de detalhes da bolsa. A issue não diz se o erro acontece no frontend (renderização/formatação de data) ou no backend (serialização/consulta).
2. A data limite de concessão é um campo **opcional** por regra de negócio. Alocações sem esse valor são válidas e não são um problema de dados a corrigir.
3. Bolsas cujas alocações têm todas a data limite preenchida já funcionam corretamente. Esse comportamento deve continuar igual.
4. A correção não deve exigir alteração no esquema do banco de dados.
5. O problema afeta apenas o campo "data limite de concessão" da alocação. Não sabemos se outros campos opcionais causam erro parecido.

## Stack Tecnológica

Não informado na issue original.

## Comandos

Não informado na issue original.
- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Não informado na issue original. A localização da tela de bolsas, do componente de visualização e do modelo/entidade de alocação é desconhecida.

## Estilo de Código

Não informado na issue original.

## Estratégia de Testes

O framework e a localização dos testes não foram informados na issue original. Níveis de teste esperados, a confirmar com a stack real:
- **Teste de regressão (unitário/componente):** visualização de uma bolsa com alocação sem data limite de concessão não gera erro, e o campo vazio aparece conforme o comportamento definido.
- **Teste de não regressão:** visualização de uma bolsa com todas as alocações com data limite preenchida continua exibindo as datas corretamente.
- **Caso misto:** bolsa com várias alocações, algumas com e outras sem data limite. Todas devem ser exibidas corretamente.
- **Integração/E2E (se existir infraestrutura):** clicar no "olhinho" na tela de bolsas abre os detalhes sem erro para os três cenários acima.

## Limites

- **Sempre:**
  - Reproduzir o erro antes de corrigir e registrar a mensagem/stack trace.
  - Tratar a data limite de concessão como possivelmente ausente em todo o fluxo de visualização.
  - Adicionar teste de regressão que cubra a alocação sem data limite.
  - Rodar os testes existentes antes de concluir.
- **Perguntar antes:**
  - Tornar a data limite de concessão obrigatória ou alterar o esquema do banco.
  - Preencher ou migrar dados existentes de alocações sem data.
  - Adicionar novas dependências (por exemplo, biblioteca de datas).
  - Mudar o comportamento de outras telas que usam a mesma data.
- **Nunca:**
  - Esconder bolsas ou alocações sem data limite para "evitar" o erro.
  - Suprimir o erro de forma genérica (try/catch silencioso) sem tratar a causa.
  - Remover ou desabilitar testes existentes.
  - Inventar um valor de data padrão que possa ser confundido com uma data real.

## Critérios de Sucesso

1. Clicar no "olhinho" de uma bolsa com pelo menos uma alocação sem data limite de concessão abre os detalhes sem erro, seja no console, na interface ou na resposta do servidor.
2. Nas alocações sem data limite, o campo aparece vazio ou com um texto indicativo, conforme definido nas Questões em Aberto.
3. Nas alocações com data limite, a data continua sendo exibida com o mesmo formato de antes.
4. Bolsas com mistura de alocações (com e sem data) exibem todas as alocações corretamente.
5. Existe pelo menos um teste automatizado que falhava antes da correção e passa depois.
6. Todos os testes existentes continuam passando.

## Questões em Aberto

1. Qual é a mensagem de erro exata e o stack trace? Ele aparece no frontend (console/tela) ou no backend (status HTTP 500, por exemplo)?
2. A data limite de concessão é de fato opcional pela regra de negócio, ou alocações sem ela são dados inconsistentes que deveriam ser corrigidos?
3. Como exibir uma alocação sem data limite: campo vazio, "-", "Não informada", "Sem data limite" ou outro texto?
4. Outras telas ou funcionalidades usam a data limite de concessão (listagem, relatórios, exportações, edição)? Elas também devem ser verificadas nesta issue?
5. Existem outros campos opcionais de alocação com o mesmo risco que devam entrar no escopo?
6. Quais são a stack, os comandos de build/teste e os caminhos dos arquivos envolvidos (tela de bolsas, componente de visualização, modelo de alocação)?
7. Há um ambiente ou bolsa específica onde o erro possa ser reproduzido (ID da bolsa de exemplo)?