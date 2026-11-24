# Spec: Atualização de gems vulneráveis apontadas pelo Dependabot

## Objetivo

O Dependabot emitiu alertas de vulnerabilidade de severidade **moderada** para algumas gems do projeto e sugeriu atualizá-las para as versões corrigidas. O objetivo é eliminar esses alertas atualizando as gems afetadas para versões sem a vulnerabilidade, sem regressões funcionais na aplicação.

**Usuários afetados:** mantenedores do projeto (segurança da cadeia de dependências) e, indiretamente, os usuários finais da aplicação, expostos às vulnerabilidades enquanto não forem corrigidas.

**Critérios de aceitação (alto nível):**
- Todas as gems citadas nos alertas do Dependabot estão em versão igual ou superior à versão corrigida indicada no alerta.
- Os alertas correspondentes aparecem como resolvidos/fechados no Dependabot.
- A aplicação continua funcionando como antes (suíte de testes passando, sem mudanças de comportamento não intencionais).

## Premissas

1. O projeto é Ruby e gerencia dependências com Bundler (`Gemfile` / `Gemfile.lock`), já que a issue fala em "gems".
2. Os alertas estão no recurso Dependabot do GitHub do repositório, e a lista exata de gems, CVEs/GHSAs e versões corrigidas pode ser consultada lá.
3. "Versões corrigidas" são as indicadas pelo próprio Dependabot em cada alerta, ou seja, a menor versão sem a vulnerabilidade.
4. A correção preferencial é a atualização mínima necessária (patch/minor), não a atualização geral de todas as dependências.
5. Algumas gems vulneráveis podem ser dependências transitivas e não estar declaradas diretamente no `Gemfile`.
6. Existem PRs automáticos do Dependabot abertos para essas gems, ou podem ser gerados. Isso não foi confirmado.
7. Se uma versão corrigida exigir mudança de versão major, de versão do Ruby ou de outra gem principal (ex.: Rails), isso sai do escopo desta issue e precisa de aprovação.

## Stack Tecnológica

- Linguagem: Ruby (inferido de "gems"). Versão não informada na issue original.
- Gerenciador de dependências: Bundler (presumido). Versão não informada na issue original.
- Framework (ex.: Rails): não informado na issue original.
- Gems afetadas e versões atuais/corrigidas: não informadas na issue original.

## Comandos

Não informado na issue original.

Os comandos de instalação, testes, lint e verificação de vulnerabilidades do projeto são desconhecidos e precisam ser confirmados. Exemplos: se o projeto usa `bundle`, `bundler-audit` ou outro executor de testes, e com quais flags.

## Estrutura do Projeto

Não informado na issue original.

Os arquivos de dependências provavelmente envolvidos (`Gemfile`, `Gemfile.lock`) são presumidos e não foram confirmados. A localização dos testes e da configuração de CI é desconhecida.

## Estilo de Código

Não informado na issue original.

Pela natureza da mudança, espera-se alteração apenas nos arquivos de dependências, sem alteração de código da aplicação. Se alguma atualização exigir ajuste de código, ele deve seguir as convenções existentes do projeto, que não constam na issue.

## Estratégia de Testes

Framework e localização dos testes: não informados na issue original.

Estratégia esperada:
- Rodar a suíte completa de testes existente após a atualização, para detectar regressões.
- Para cada gem atualizada, revisar o changelog entre a versão atual e a corrigida em busca de mudanças incompatíveis, e testar com atenção as áreas da aplicação que usam essa gem.
- Validar que os alertas deixam de existir, pelo status no Dependabot ou por ferramenta de auditoria de dependências, se o projeto tiver uma (não informado).
- Garantir que o pipeline de CI passa. A existência e a configuração do CI não foram informadas.

## Limites

- **Sempre:**
  - Atualizar apenas as gems apontadas nos alertas e as dependências estritamente necessárias para resolvê-las.
  - Commitar `Gemfile.lock` junto com qualquer alteração no `Gemfile`.
  - Rodar a suíte de testes antes de commitar.
  - Referenciar os alertas do Dependabot (IDs GHSA/CVE) na descrição do PR.
- **Perguntar antes:**
  - Atualizações de versão major de qualquer gem.
  - Atualização do Ruby, do Bundler ou do framework principal.
  - Adição ou remoção de gems.
  - Alteração de código da aplicação para acomodar mudanças de API das gems.
  - Alteração na configuração de CI ou do Dependabot.
  - Ignorar/descartar um alerta em vez de corrigi-lo.
- **Nunca:**
  - Rodar `bundle update` geral sem restrição, atualizando dependências fora do escopo.
  - Remover ou desabilitar testes que falhem após a atualização sem aprovação.
  - Fechar alertas do Dependabot manualmente sem que a vulnerabilidade esteja de fato corrigida.
  - Commitar segredos ou credenciais.

## Critérios de Sucesso

1. Para cada alerta moderado listado pelo Dependabot, a gem correspondente no `Gemfile.lock` está em versão maior ou igual à versão corrigida indicada no alerta.
2. Nenhum alerta do Dependabot referente a essas gems permanece aberto após o merge na branch padrão.
3. A suíte de testes completa passa sem novas falhas em relação ao estado anterior à mudança.
4. O CI (se existir) passa no PR.
5. Nenhuma gem fora do escopo dos alertas teve sua versão alterada, exceto dependências transitivas exigidas pela resolução, que devem ser listadas no PR.
6. A descrição do PR lista cada gem atualizada com a versão anterior, a nova versão e o identificador do alerta (GHSA/CVE).

## Perguntas em Aberto

1. **Quais gems exatamente** foram apontadas pelo Dependabot, com quais versões atuais, versões corrigidas e identificadores (GHSA/CVE)? A issue não lista nenhuma.
2. Há PRs do Dependabot já abertos para essas gems? Devemos aproveitá-los (revisar e mergear) ou consolidar tudo em um único PR?
3. Algum dos alertas é de dependência transitiva? Se sim, a gem que a puxa permite a versão corrigida sem upgrade major?
4. Alguma versão corrigida exige upgrade major, novo Ruby ou nova versão do framework? Se sim, isso fica nesta issue ou em outra?
5. Quais são os comandos de instalação, teste e auditoria do projeto, e existe CI que deve passar?
6. Existe algum alerta que deva ser descartado (ex.: gem só usada em desenvolvimento/teste, ou código vulnerável não utilizado) em vez de corrigido?
7. Há prazo ou política de segurança definida para correção de vulnerabilidades moderadas?
8. Existem ambientes (staging/produção) onde a atualização precisa ser validada manualmente antes do deploy?