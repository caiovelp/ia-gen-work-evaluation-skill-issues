# Spec: Atualização da gem `carrierwave` para versão >= 3.0.7 (alerta do Dependabot)

## Objetivo

Corrigir a vulnerabilidade apontada pelo Dependabot na gem `carrierwave` atualizando-a para uma versão **>= 3.0.7**, conforme a recomendação do alerta.

- **Por quê:** a versão atual da gem tem uma vulnerabilidade de segurança conhecida. O identificador (CVE/GHSA), a severidade e o vetor não foram informados na issue.
- **Quem é afetado:** usuários e mantenedores da aplicação que usa `carrierwave` para upload e armazenamento de arquivos.
- **Como é o sucesso:** o alerta do Dependabot é encerrado. A aplicação continua funcionando, e o upload, o processamento e a exibição de arquivos se comportam como antes.

**Critérios de aceitação (rascunho):**
- O lockfile de dependências registra `carrierwave` em versão >= 3.0.7.
- O alerta do Dependabot correspondente é resolvido ou fechado automaticamente.
- A suíte de testes existente passa sem regressões.
- Os fluxos de upload que usam `carrierwave` continuam funcionando.

## Premissas

1. O projeto é uma aplicação Ruby que gerencia dependências com Bundler (`Gemfile` / `Gemfile.lock`). A issue não confirma isso, mas é o padrão para gems Ruby.
2. A versão atualmente instalada de `carrierwave` é inferior a 3.0.7. Não se sabe se é da série 2.x ou 3.x.
3. O alerta provavelmente se refere a uma vulnerabilidade divulgada em 2024 sobre bypass da allowlist de content-type, com risco de XSS (possivelmente CVE-2024-29034). Essa falha foi corrigida em 3.0.7 e também em 2.2.6. A premissa não foi confirmada e deve ser verificada no alerta.
4. A atualização deve ficar restrita a `carrierwave` e às dependências transitivas estritamente necessárias, sem atualizações amplas de outras gems.
5. Não há patches locais nem monkey patches sobre `carrierwave` que impeçam a atualização.
6. O projeto tem uma suíte de testes automatizados e um pipeline de CI que validam a mudança.

## Stack Tecnológica

- Linguagem: Ruby (versão não informada).
- Framework: possivelmente Ruby on Rails (não confirmado).
- Gem alvo: `carrierwave`, versão atual desconhecida, versão alvo >= 3.0.7.
- Gems relacionadas possivelmente afetadas: não informado na issue original (ex.: `mini_magick`, `fog-aws`, `ssrf_filter`, `marcel`).

## Comandos

Não informado na issue original.

- Instalação/atualização de dependências: desconhecido.
- Testes: desconhecido.
- Lint: desconhecido.
- Build/execução local: desconhecido.

## Estrutura do Projeto

Não informado na issue original.

- Arquivos de dependências esperados: `Gemfile` e `Gemfile.lock` (premissa, não confirmado).
- Localização dos uploaders: desconhecida.
- Localização dos testes: desconhecida.

## Estilo de Código

Não informado na issue original.

## Estratégia de Testes

Os detalhes concretos não constam na issue original. Em nível de requisito, a validação deve cobrir:

- **Testes automatizados existentes:** a suíte completa deve passar após a atualização. Framework e comando são desconhecidos.
- **Uploaders:** os testes que cobrem as classes uploader, como validações de extensão e content-type e versões ou processamentos de imagem, devem passar.
- **Regressão funcional manual:** um upload válido deve ser aceito, e um arquivo com tipo não permitido deve ser rejeitado.
- **Verificação de segurança:** confirmar que o Dependabot, ou ferramenta equivalente, não aponta mais a vulnerabilidade.

Não se sabe se existe cobertura de testes para os uploaders.

## Limites

- **Sempre:**
  - Restringir a mudança à atualização de `carrierwave` e às dependências estritamente necessárias.
  - Rodar a suíte de testes antes do merge.
  - Revisar o changelog do `carrierwave` entre a versão atual e a versão alvo.
- **Perguntar antes:**
  - Atualizar a versão major (ex.: de 2.x para 3.x), se o projeto estiver na série 2.x.
  - Alterar o código dos uploaders ou das configurações de armazenamento para acomodar breaking changes.
  - Atualizar outras gems além das exigidas pela resolução de dependências.
  - Mudar a versão do Ruby ou do Rails.
- **Nunca:**
  - Ignorar ou silenciar o alerta do Dependabot sem corrigir a vulnerabilidade.
  - Remover ou desabilitar testes que falharem após a atualização sem aprovação.
  - Commitar credenciais de armazenamento (ex.: chaves de cloud).

## Critérios de Sucesso

1. `carrierwave` está fixada no lockfile em versão >= 3.0.7. Se a equipe optar por permanecer na série 2.x, a versão deve conter a correção, condicionado à Questão Aberta 2.
2. O alerta do Dependabot referente a `carrierwave` está fechado.
3. Toda a suíte de testes e o pipeline de CI passam.
4. O upload de arquivos válidos continua funcionando em todos os uploaders existentes.
5. As validações de tipo de arquivo (allowlist/denylist de extensão e content-type) continuam rejeitando arquivos não permitidos.
6. Nenhuma outra dependência foi atualizada além do necessário, ou cada atualização adicional está justificada.

## Questões em Aberto

1. **Identificação:** qual é o identificador exato da vulnerabilidade (CVE/GHSA) e qual a sua severidade? A resposta confirma ou descarta a Premissa 3.
2. **Versão atual e série:** qual versão de `carrierwave` está em uso hoje? Se for da série 2.x:
   - É aceitável migrar para a 3.x, que é uma mudança major com possíveis breaking changes?
   - Ou a equipe prefere uma versão corrigida da série 2.x (ex.: 2.2.6), contrariando a sugestão literal do Dependabot?
3. **Compatibilidade:** as versões de Ruby e Rails do projeto são compatíveis com `carrierwave` >= 3.0.7?
4. **Uso da gem:** quais uploaders e backends de armazenamento (local, fog, S3 etc.) usam `carrierwave`? Algum deles depende de comportamento alterado entre as versões?
5. **Mitigação adicional:** os uploaders já usam allowlist de content-type? Além da atualização, é necessário revisar essas configurações?
6. **Impacto em dados existentes:** é preciso verificar se arquivos já enviados exploraram a vulnerabilidade, por exemplo arquivos maliciosos já armazenados?
7. **Cobertura de testes:** existe cobertura automatizada para os fluxos de upload, ou a validação dependerá de teste manual?
8. **Prazo:** há prioridade ou prazo de correção definido pela política de segurança da equipe?