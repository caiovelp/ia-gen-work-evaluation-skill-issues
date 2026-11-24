# Spec: Atualização da gem Active_Scaffold

## Objetivo

Hoje o projeto aponta para um **commit** do Active_Scaffold, e não para uma versão publicada da gem. A gem também está defasada. Esta issue tem dois objetivos:

1. **Fixar a versão.** Substituir a referência ao commit por uma versão publicada (release) do Active_Scaffold.
2. **Atualizar a gem.** Subir até a versão mais recente, hoje a **4.3.0**, em saltos incrementais. Cada salto precisa de:
   - testes;
   - correção dos bugs encontrados;
   - um PR próprio;
   - deploy em produção.

**Motivação:** esta atualização prepara o terreno para a futura atualização do Rails.

**Usuários afetados:** quem usa as telas e funcionalidades construídas com Active_Scaffold. Quais são essas telas não foi informado na issue original.

**Critérios de aceitação (por história):**
- Como mantenedor, quero que a dependência aponte para uma versão publicada, para ter builds reprodutíveis e rastreáveis.
- Como mantenedor, quero o Active_Scaffold na 4.3.0, para não bloquear a atualização do Rails.
- Como usuário, quero que as telas continuem funcionando após cada salto, sem regressões em produção.

## Premissas

1. O projeto é uma aplicação Ruby on Rails que declara suas dependências via Bundler (`Gemfile` / `Gemfile.lock`). O caminho exato não está confirmado.
2. A referência ao commit é feita por uma opção como `git:`/`github:` com `ref:` no `Gemfile`.
3. O primeiro passo é fixar a versão publicada **equivalente ou mais próxima** do commit atual, sem pular de versão de uma vez. Assim, a fixação fica separada do upgrade.
4. "Saltos de versão" significa passar pelas versões intermediárias publicadas entre a versão fixada e a 4.3.0. A granularidade (major, minor ou patch) ainda não foi definida.
5. Cada salto é uma entrega independente: um PR, um deploy em produção e uma validação antes do próximo salto.
6. A versão atual do Rails será mantida durante toda a issue. Atualizar o Rails está fora de escopo.
7. A 4.3.0 é compatível com as versões atuais de Rails e Ruby do projeto. Isso precisa ser verificado, porque pode exigir parar num salto anterior.
8. Existe algum ambiente de homologação/staging antes de produção. Não está confirmado.

## Stack Tecnológica

- **Linguagem/Framework:** Ruby on Rails (premissa). As versões de Ruby e Rails não foram informadas na issue original.
- **Gem alvo:** `active_scaffold`, que hoje aponta para um commit (hash não informado) e deve chegar à versão 4.3.0.
- **Gerenciador de dependências:** Bundler (premissa).
- **Demais dependências relevantes** (ex.: jQuery, Sprockets/Propshaft, outras gems acopladas ao Active_Scaffold): não informado na issue original.

## Comandos

Não informado na issue original.

- **Build:** desconhecido
- **Testes:** desconhecido
- **Lint:** desconhecido
- **Dev:** desconhecido
- **Atualização da dependência:** desconhecido (provavelmente via Bundler, a confirmar)
- **Deploy em produção:** desconhecido

## Estrutura do Projeto

Não informado na issue original.

Os locais a seguir ainda precisam ser identificados:
- arquivo de dependências (`Gemfile` presumido);
- controllers e configurações que usam Active_Scaffold;
- overrides de views e helpers do Active_Scaffold;
- assets (JS/CSS) da gem;
- diretório de testes.

## Estilo de Código

Não informado na issue original.

## Estratégia de Testes

A issue exige testes a cada salto de versão, mas não detalha como. Estrutura proposta, a confirmar:

- **Suíte automatizada existente:** rodar a suíte completa a cada salto. Framework, localização e cobertura não foram informados na issue original.
- **Testes manuais/regressão:** percorrer as telas que usam Active_Scaffold após cada salto. Validar:
  - listagem, busca, ordenação e paginação;
  - criação, edição e exclusão;
  - ações customizadas;
  - subformulários e associações;
  - exportações, se houver.
- **Changelog/notas de versão:** revisar as notas de cada versão intermediária para mapear breaking changes e deprecações antes de testar.
- **Warnings de depreciação:** registrar os warnings que surgirem em cada salto.
- **Validação pós-deploy:** monitorar produção após cada deploy antes de iniciar o próximo salto. Critérios de monitoramento não informados.

## Limites

- **Sempre:**
  - Fazer um PR por salto de versão.
  - Rodar os testes antes de abrir o PR.
  - Validar em produção antes do próximo salto.
  - Atualizar o arquivo de lock junto com a declaração da dependência.
  - Registrar no PR a versão de origem, a de destino e os bugs corrigidos.
- **Perguntar antes:**
  - Atualizar outras gems além do Active_Scaffold, inclusive dependências transitivas que mudem de versão.
  - Alterar a versão de Rails ou Ruby.
  - Pular versões intermediárias.
  - Remover ou reescrever overrides de views e helpers.
  - Alterar o comportamento visível de telas.
- **Nunca:**
  - Voltar a apontar a gem para commit ou branch.
  - Juntar vários saltos de versão num único PR/deploy.
  - Remover ou desabilitar testes que falham sem aprovação.
  - Atualizar o Rails dentro desta issue.

## Critérios de Sucesso

1. A dependência `active_scaffold` aponta para uma **versão publicada**, sem referência a commit, branch ou repositório git.
2. A versão resolvida no arquivo de lock é **4.3.0**.
3. Cada salto intermediário teve:
   - um **PR próprio**;
   - a **suíte de testes passando**;
   - os **bugs encontrados corrigidos**;
   - **deploy em produção** concluído e validado.
4. Nenhuma regressão funcional conhecida nas telas que usam Active_Scaffold após o último salto.
5. Os warnings de depreciação do Active_Scaffold restantes estão documentados ou resolvidos.
6. Está registrado se a versão final do Active_Scaffold permite atualizar o Rails (e para quais versões), como insumo para a issue de upgrade do Rails.

## Questões em Aberto

1. Qual é o commit atual referenciado, e de qual repositório/fork? Ele contém patches próprios que não existem em nenhuma versão publicada?
2. Qual versão publicada deve ser usada na fixação inicial: a imediatamente anterior ou posterior ao commit atual, ou outra?
3. Qual a granularidade dos saltos: por major (ex.: 3.x → 4.0), por minor, ou passando por todas as versões publicadas? Existe uma lista definida de versões intermediárias?
4. Quais são as versões atuais de Ruby e Rails? A 4.3.0 do Active_Scaffold é compatível com elas, ou algum salto exige primeiro atualizar o Rails?
5. Existe suíte de testes automatizada cobrindo as telas com Active_Scaffold? Qual framework e cobertura?
6. Existe ambiente de homologação/staging? Qual o processo e o comando de deploy em produção?
7. Quais critérios definem que um salto está validado em produção (tempo de observação, métricas, ausência de erros)?
8. Qual o plano de rollback caso um salto cause problemas em produção?
9. Existem overrides de views, helpers ou JS do Active_Scaffold, ou plugins/gems que dependem dele, que precisam de atenção especial?
10. Há prazo ou janela de deploy definida para cada salto?
11. A fixação da versão (item 1 do objetivo) deve ser um PR/deploy separado do primeiro salto de atualização?