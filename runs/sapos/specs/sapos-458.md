# Spec: Atualização da gem `rack` para corrigir vulnerabilidades apontadas pelo Dependabot

## Objetivo

O Dependabot apontou vulnerabilidades na versão da gem `rack` usada pelo projeto e sugeriu atualizar para a versão **>= 2.2.8.1**.

**O que será feito:** atualizar a dependência `rack` para uma versão corrigida, sem quebrar a aplicação nem as gems que dependem de `rack`.

**Por que:** eliminar as vulnerabilidades conhecidas da versão atual e encerrar os alertas do Dependabot.

**Quem é afetado:** mantenedores do projeto (alertas de segurança abertos) e usuários finais da aplicação (exposição às vulnerabilidades).

**Critérios de aceitação (história):**
- Como mantenedor, quero que a gem `rack` esteja numa versão >= 2.2.8.1, para que os alertas de segurança do Dependabot sejam resolvidos sem regressões.

## Premissas

1. O projeto é Ruby e gerencia dependências com Bundler (`Gemfile` / `Gemfile.lock`), já que o alerta veio do Dependabot para uma gem.
2. A versão atual de `rack` está na série 2.x, abaixo de 2.2.8.1. A sugestão do Dependabot é a 2.2.8.1, e não uma 3.x.
3. `rack` é uma dependência **transitiva**, provavelmente via Rails, Sinatra, Puma ou outro framework web. Nesse caso ela pode não constar explicitamente no `Gemfile`, apenas no `Gemfile.lock`.
4. A correção desejada é a menor mudança possível: um patch dentro da série 2.2.x, sem migrar para `rack` 3.x.
5. Os alertas provavelmente correspondem às vulnerabilidades corrigidas na 2.2.8.1 (fevereiro de 2024), ligadas a negação de serviço / ReDoS no parsing de cabeçalhos e de requisições multipart, como CVE-2024-25126, CVE-2024-26141 e CVE-2024-26146. **Isso não está confirmado na issue.**
6. Existe uma suíte de testes automatizada que pode ser usada para validar a atualização.

## Stack Tecnológica

- Linguagem: Ruby (inferido pelo uso de gems). Versão não informada na issue original.
- Gerenciador de dependências: Bundler (presumido).
- Gem alvo: `rack`. Versão atual desconhecida. Versão mínima exigida: **2.2.8.1**.
- Framework web e demais dependências: Não informado na issue original.

## Comandos

Não informado na issue original.

- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Atualização de dependências: desconhecido. O mais provável é um comando do Bundler, mas a forma exata depende de como `rack` é declarada no projeto. Ver Perguntas em Aberto.

## Estrutura do Projeto

Não informado na issue original.

Arquivos provavelmente envolvidos (presumidos, não confirmados):
- `Gemfile`: declaração de dependências, caso `rack` ou a gem que a puxa esteja fixada ali.
- `Gemfile.lock`: versão resolvida de `rack`.

## Estilo de Código

Não informado na issue original.

A mudança esperada fica restrita a arquivos de dependência. Se for preciso declarar `rack` explicitamente no `Gemfile`, deve-se seguir o padrão de declaração de versão já usado no projeto, que é desconhecido.

## Estratégia de Testes

Não há informação na issue original sobre framework de testes, localização dos testes ou cobertura.

Validação esperada para esta mudança:
- **Suíte completa existente:** deve passar sem novas falhas após a atualização.
- **Smoke test da aplicação:** subir a aplicação e fazer requisições básicas, porque `rack` está no núcleo do tratamento de requisições HTTP.
- **Áreas de atenção:** fluxos que dependem de parsing de requisições, como upload multipart / formulários, cabeçalhos `Accept` / `Range` e cookies. Essas são as áreas que provavelmente mudaram no patch (ver Premissa 5).
- **Verificação da resolução:** confirmar no `Gemfile.lock` que a versão resolvida de `rack` é >= 2.2.8.1.

## Limites

- **Sempre:**
  - Restringir a mudança à atualização de `rack` e ao mínimo de dependências necessárias para resolvê-la.
  - Rodar a suíte de testes completa antes de concluir.
  - Fazer commit do `Gemfile.lock` atualizado.
  - Referenciar os alertas do Dependabot no PR.
- **Perguntar antes:**
  - Migrar para `rack` 3.x, que tem mudanças incompatíveis.
  - Atualizar outras gems, como o framework web ou o servidor de aplicação, caso a restrição de versão delas impeça chegar a `rack` >= 2.2.8.1.
  - Adicionar uma declaração explícita de `rack` no `Gemfile`, se hoje ela for apenas transitiva.
  - Alterar a versão do Ruby ou do Bundler.
- **Nunca:**
  - Ignorar ou descartar os alertas do Dependabot sem resolvê-los.
  - Remover ou desabilitar testes que falharem após a atualização sem aprovação.
  - Fazer atualizações amplas e não relacionadas, como uma atualização geral de todas as gems, junto com esta correção.

## Critérios de Sucesso

1. O `Gemfile.lock` resolve `rack` para uma versão **>= 2.2.8.1**, de preferência dentro da série 2.2.x (Premissa 4).
2. Os alertas do Dependabot relacionados a `rack` são fechados automaticamente ou deixam de ser reportados para a versão resolvida.
3. A suíte de testes existente passa sem novas falhas em relação ao estado anterior à mudança.
4. A aplicação inicia e responde normalmente a requisições básicas.
5. O diff limita-se a arquivos de dependência (`Gemfile.lock` e, se aprovado, `Gemfile`), sem alterar código de aplicação, salvo necessidade justificada e aprovada.

## Perguntas em Aberto

1. **Quais são exatamente os alertas?** Quais CVEs / GHSA o Dependabot listou, e qual a severidade? Isso confirma ou corrige a Premissa 5 e define quais áreas testar com mais atenção.
2. **Qual a versão atual de `rack`** no `Gemfile.lock`?
3. **`rack` é dependência direta ou transitiva?** Se for transitiva, qual gem a puxa (Rails, Sinatra, Puma etc.)? A restrição de versão dessa gem permite chegar a 2.2.8.1 sem atualizá-la?
4. **2.2.8.1 é suficiente ou o alvo deve ser a versão 2.2.x mais recente?** Versões posteriores da série 2.2.x podem corrigir vulnerabilidades adicionais reportadas depois desse alerta.
5. **Existe interesse ou restrição quanto a migrar para `rack` 3.x?** A premissa é que não, por ora.
6. **Já existe um PR automático do Dependabot** para essa atualização? Ele deve ser aproveitado ou a mudança deve ser feita manualmente?
7. **Quais comandos de teste e build** o projeto usa, e há CI que precise passar antes do merge?
8. **Versões de Ruby e Bundler** do projeto: há alguma restrição que limite as versões de `rack` disponíveis?
9. **Há outros alertas do Dependabot** abertos que devam ser tratados junto, ou esta issue cobre somente `rack`?