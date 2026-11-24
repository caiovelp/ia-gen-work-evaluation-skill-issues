# Spec: Correção do erro interno ao visualizar detalhes de um desligamento

## Objetivo

Corrigir o erro interno (internal error) gerado ao clicar no ícone de visualização ("olhinho") de uma tupla na listagem de desligamentos. O usuário deve conseguir abrir e consultar as informações detalhadas de um desligamento sem que o sistema falhe.

**Usuário:** quem consulta registros de desligamento no sistema (perfil exato não informado na issue).

**Comportamento atual:** ao clicar no "olhinho" de um desligamento, é exibido/gerado um internal error.

**Comportamento esperado:** ao clicar no "olhinho", as informações do desligamento selecionado são exibidas corretamente.

**Critérios de aceitação (propostos):**
- Clicar no "olhinho" de qualquer desligamento existente exibe seus detalhes sem erro interno.
- O erro não é reproduzível com os registros que hoje o disparam.
- A correção não quebra a listagem de desligamentos nem as demais ações da tupla (se existirem).

## Premissas

1. "Desligamentos" é uma tela/módulo de uma aplicação web que lista registros em formato de tabela, e "tupla" se refere a uma linha dessa tabela.
2. O "olhinho" é um ícone de ação que abre uma tela, página ou modal de detalhes do registro.
3. "Internal error" corresponde a uma falha no servidor (provavelmente HTTP 500) ao buscar ou renderizar os detalhes, e não a um erro de validação esperado.
4. O erro ocorre para todos os desligamentos, ou pelo menos para um subconjunto reproduzível. A issue não esclarece qual dos dois casos.
5. A correção deve preservar os dados e o comportamento atual de exibição, sem redesenhar a tela de detalhes.

## Stack Tecnológica

Não informado na issue original.

## Comandos

Não informado na issue original.
- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Não informado na issue original. A localização do módulo de desligamentos, da rota/controller de detalhes e do template/componente de visualização é desconhecida.

## Estilo de Código

Não informado na issue original.

## Estratégia de Testes

Não informado na issue original. Abordagem proposta, a confirmar com a stack do projeto:
- Antes da correção, escrever um teste (de integração ou de requisição) que reproduza o erro ao acessar os detalhes de um desligamento e que falhe com o comportamento atual.
- Cobrir casos de borda que possam causar o erro, como campos opcionais nulos, relacionamentos ausentes (por exemplo, funcionário ou motivo removido) e datas vazias.
- Validar manualmente o fluxo completo: listagem → clique no "olhinho" → exibição dos detalhes.

## Limites

- **Sempre:** reproduzir o erro antes de corrigir; adicionar um teste de regressão; rodar a suíte de testes existente antes de concluir; tratar dados ausentes ou nulos de forma segura na exibição.
- **Perguntar antes:** alterar o esquema do banco de dados ou migrar dados; mudar regras de permissão de acesso aos desligamentos; adicionar dependências; alterar o layout ou o conteúdo exibido na tela de detalhes além do necessário para a correção.
- **Nunca:** mascarar o erro sem tratar a causa (por exemplo, capturar a exceção e exibir uma tela vazia); expor stack traces ou dados sensíveis ao usuário; remover ou desabilitar testes existentes.

## Critérios de Sucesso

- [ ] O erro interno é reproduzido em ambiente de desenvolvimento ou teste, e sua causa raiz é identificada e documentada.
- [ ] Ao clicar no "olhinho" de um desligamento, os detalhes são exibidos com sucesso (por exemplo, resposta HTTP 200 e conteúdo renderizado).
- [ ] Desligamentos com campos opcionais ou relacionamentos ausentes também exibem os detalhes sem erro.
- [ ] Existe um teste automatizado que falhava antes da correção e passa depois dela.
- [ ] A listagem de desligamentos e as demais funcionalidades do módulo continuam funcionando, e a suíte de testes existente passa.

## Questões em Aberto

1. **Reprodução:** o erro ocorre para todos os desligamentos ou apenas para alguns? Se for apenas para alguns, quais (por exemplo, registros antigos, de um tipo de desligamento específico ou com algum campo vazio)?
2. **Ambiente:** em qual ambiente o erro foi observado (produção, homologação, local)? Desde quando ocorre? Houve deploy ou migração recente?
3. **Logs:** há stack trace ou log do servidor associado ao internal error? Isso ajudaria a identificar a causa raiz.
4. **Perfil do usuário:** o erro depende do perfil ou permissão de quem acessa?
5. **Conteúdo esperado:** quais informações a tela de detalhes deve exibir? Existe uma referência de comportamento anterior funcionando?
6. **Stack e repositório:** quais são o framework, a linguagem, os comandos de build e teste, e o caminho do módulo de desligamentos?
7. **Escopo:** o "olhinho" de outras listagens do sistema também apresenta o problema, ou o erro é exclusivo de desligamentos?