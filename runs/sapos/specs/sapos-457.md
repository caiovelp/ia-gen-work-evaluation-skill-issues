# Spec: Atualização das gems rails, actionpack e activestorage para corrigir vulnerabilidades (alerta do Dependabot)

## Objetivo

Corrigir as vulnerabilidades que o Dependabot apontou nas gems `rails`, `actionpack` e `activestorage`, atualizando-as para uma versão **>= 7.0.8.1**, a versão sugerida no alerta.

- **Por quê:** o projeto usa versões dessas gems com vulnerabilidades conhecidas. A atualização remove essa exposição de segurança.
- **Quem se beneficia:** os mantenedores do projeto e os usuários finais da aplicação, que deixam de estar expostos às vulnerabilidades.
- **Como é o sucesso:** os alertas do Dependabot para essas três gems são encerrados e a aplicação continua funcionando como antes.

**Critérios de aceitação (história de usuário):**
- Como mantenedor, quero que `rails`, `actionpack` e `activestorage` estejam em versão >= 7.0.8.1. Assim os alertas de segurança do Dependabot são resolvidos sem regressões funcionais.

## Premissas

1. O projeto é uma aplicação Ruby on Rails que gerencia dependências com Bundler (`Gemfile` / `Gemfile.lock`).
2. A versão atual das gems é da série **7.0.x**, anterior à 7.0.8.1. Isso é deduzido da versão sugerida pelo alerta; a issue não informa a versão atual.
3. O objetivo é a **menor atualização que corrige o problema**: um patch dentro da série 7.0 (7.0.8.1 ou um patch posterior da mesma série). Não é uma migração para Rails 7.1+ ou 8.x.
4. As gems irmãs do Rails (`activesupport`, `activerecord`, `actionview`, `activejob`, `actioncable`, `actionmailer`, `actionmailbox`, `actiontext`, `railties` etc.) serão atualizadas para a mesma versão. O Rails exige versões alinhadas entre seus componentes.
5. A atualização de patch não exige mudanças de código na aplicação. Pode haver ajustes pontuais se algum teste revelar incompatibilidade.
6. A versão 7.0.8.1 do Rails (fevereiro de 2024) corrigiu advisories de segurança em `actionpack` e `activestorage`, provavelmente CVE-2024-26143 e CVE-2024-26144. **Isso é hipótese e precisa ser confirmado com os alertas reais do Dependabot**, pois a issue não lista os identificadores.
7. Existe uma suíte de testes automatizados e algum pipeline de CI. Os detalhes não aparecem na issue.

## Stack Tecnológica

- Ruby on Rails, série 7.0.x (versão exata atual desconhecida)
- Gems afetadas: `rails`, `actionpack`, `activestorage`
- Versão-alvo mínima: `7.0.8.1`
- Versão do Ruby: Não informado na issue original.
- Banco de dados e demais dependências: Não informado na issue original.

## Comandos

Não informado na issue original.

Os comandos de build, testes, lint e servidor de desenvolvimento são desconhecidos. Seria preciso confirmar, por exemplo:
- Comando de atualização das gems: desconhecido (provavelmente via Bundler, a confirmar)
- Testes: desconhecido
- Lint / auditoria de segurança: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Não informado na issue original.

Os arquivos provavelmente envolvidos são `Gemfile` e `Gemfile.lock`, na raiz do projeto, mas a localização não foi confirmada.

## Estilo de Código

Não informado na issue original.

A mudança esperada fica restrita a arquivos de dependências, então convenções de estilo de código devem ter pouco impacto.

## Estratégia de Testes

Não informado na issue original.

Abordagem esperada, a ajustar conforme o projeto:
- Rodar a **suíte de testes completa** antes e depois da atualização para detectar regressões.
- Dar atenção especial às áreas ligadas às gems atualizadas:
  - **actionpack:** controllers, roteamento, helpers (incluindo helpers de tradução/i18n), tratamento de requisições.
  - **activestorage:** upload, download, exibição de anexos e geração de URLs de arquivos, se o projeto usar Active Storage.
- Fazer verificação manual dos fluxos principais em ambiente de desenvolvimento ou staging, se houver.
- Framework de testes e meta de cobertura: desconhecidos.

## Limites

- **Sempre:**
  - Atualizar `rails`, `actionpack` e `activestorage` para versão >= 7.0.8.1.
  - Manter todas as gems do Rails na mesma versão.
  - Versionar juntos o `Gemfile` (se necessário) e o `Gemfile.lock`.
  - Rodar a suíte de testes antes de commitar.
  - Referenciar a issue e os alertas do Dependabot no PR.
- **Perguntar antes:**
  - Subir de série (7.0 → 7.1, 7.2 ou 8.x) em vez de aplicar só o patch.
  - Atualizar outras gems além das necessárias para resolver as dependências do Rails.
  - Alterar a versão do Ruby.
  - Fazer mudanças de código na aplicação para acomodar a atualização.
  - Alterar configuração de CI.
- **Nunca:**
  - Remover ou desabilitar testes que falharem após a atualização sem aprovação.
  - Ignorar ou dispensar os alertas do Dependabot sem corrigir a vulnerabilidade.
  - Commitar segredos ou credenciais.
  - Fazer atualizações amplas e não relacionadas (como um `bundle update` geral) no mesmo PR.

## Critérios de Sucesso

1. `Gemfile.lock` registra `rails`, `actionpack` e `activestorage` em versão **>= 7.0.8.1**.
2. Todas as demais gems do framework Rails estão na mesma versão que `rails`.
3. Os alertas do Dependabot referentes a essas três gems estão fechados ou resolvidos no repositório.
4. A suíte de testes passa sem novas falhas em relação ao estado anterior à atualização.
5. A aplicação inicia normalmente e os fluxos que usam controllers/views (actionpack) e anexos (activestorage) continuam funcionando.
6. Nenhuma gem fora do escopo foi atualizada sem justificativa registrada no PR.
7. Se houver ferramenta de auditoria de dependências no projeto, ela não reporta mais essas vulnerabilidades.

## Questões em Aberto

1. Qual é a versão atual de `rails`, `actionpack` e `activestorage` no projeto?
2. Quais são os identificadores exatos (CVE/GHSA) dos alertas do Dependabot? Confirmar se são CVE-2024-26143 (actionpack) e CVE-2024-26144 (activestorage) ou outros.
3. O alvo deve ser exatamente a série 7.0 (7.0.8.1 ou o patch mais recente da 7.0)? Ou o time prefere aproveitar para migrar para uma série mais nova e ainda suportada? A série 7.0 já está fora de suporte de segurança do Rails, o que pode motivar uma migração maior em outra issue.
4. O `Gemfile` fixa a versão do Rails de forma que exija edição manual (por exemplo, `"7.0.4"` exato)? Ou basta atualizar o `Gemfile.lock`?
5. Quais são os comandos de teste, lint e build, e qual é o pipeline de CI do projeto?
6. O projeto usa Active Storage em produção? Quais fluxos devem ser validados manualmente?
7. Há outros alertas do Dependabot abertos que devam ser tratados no mesmo PR, ou o escopo é estritamente estas três gems?
8. Existe ambiente de staging para validar a atualização antes do deploy em produção?