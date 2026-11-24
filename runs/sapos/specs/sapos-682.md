# Especificação: Separar as checagens estáticas da matriz de testes do CI e vigiar o audit semanalmente

## Objetivo

Reorganizar o workflow de CI para que as checagens estáticas (audit de dependências, lint, análise de segurança e verificação de autoload) rodem **uma vez**, num job próprio e independente da matriz de navegadores. Também adicionar uma execução semanal do audit, para detectar CVEs publicadas mesmo sem push.

**Problemas atuais que motivam a mudança:**

- `Audit` (bundle-audit) e `Lint` (rubocop) rodam dentro do job `test`, que é uma matriz Chrome + Firefox. Cada um executa duas vezes por push com resultado idêntico, embora nenhum dependa de navegador ou de banco.
- Uma falha nesses passos aborta os dois jobs da matriz **antes** de `Run tests`. A rodada termina sem informação sobre a suíte: o vermelho barato esconde o resultado caro.
- O audit depende do tempo, não do código. Uma CVE nova torna o lock vulnerável sem push, e o CI só roda no push. O Dependabot alerta, mas não barra.
- O `brakeman` está no Gemfile e nenhum workflow o executa. O `zeitwerk:check`, relevante desde a #680 (que pôs `lib/` no eager load), também não roda em lugar nenhum.

**Quem se beneficia:** os mantenedores e contribuidores, que passam a receber sempre o resultado da suíte e das checagens de forma independente, e passam a ser avisados de vulnerabilidades em repositório parado.

**Critérios de aceitação (requisitos):**

1. Existe um job `checks`:
   - sem serviço MariaDB e sem navegador;
   - com `BUNDLE_WITHOUT=production`;
   - em paralelo com `test` e **sem `needs`** entre os dois.
2. O job `checks` executa os passos `Audit`, `Lint`, `Brakeman` e `Zeitwerk`.
   - `Zeitwerk` roda `db:schema:load zeitwerk:check` em SQLite. O esquema é necessário porque o eager load lê colunas via active_scaffold.
3. `Brakeman` roda em modo relatório (`--no-exit-on-warn`) e não reprova o job por avisos.
   - Depois que o mantenedor triar os avisos, ele passa a ser portão, com um `config/brakeman.ignore` anotado. Essa transição é etapa posterior, igual ao que a #644 fez com o rubocop.
4. Um gatilho `schedule` semanal executa **somente** o audit. Os jobs `test`, `seed`, `smoke-test` e os demais passos de `checks` não rodam nesse gatilho.
5. O job `test` contém apenas a suíte de testes, sem `Audit` nem `Lint`.
6. O comentário do workflow que justifica audit/lint dentro de `test` ("rápido e falha barato") é removido ou atualizado.

## Premissas

1. O CI é GitHub Actions, dado o uso de `schedule`, matriz, jobs e Dependabot. O caminho exato do arquivo de workflow não é informado.
2. Há um único arquivo de workflow contendo `test`, `seed` e `smoke-test`. Se houver mais de um, só o que contém `test` é alterado.
3. O adaptador SQLite está disponível nos grupos do Gemfile carregados com `BUNDLE_WITHOUT=production`, pois a issue afirma que o `zeitwerk:check` roda em SQLite.
4. Os passos `Audit` e `Lint` são movidos para `checks` com os mesmos comandos e flags usados hoje em `test`, sem mudar o comportamento.
5. "Portão" via branch protection exigindo os status de `checks` e `test` é configuração do repositório no GitHub e fica a cargo do mantenedor. Não faz parte da mudança de código.
6. O job `checks` não usa matriz: roda uma única vez por evento.
7. Na execução agendada, é aceitável que o audit rode como um passo do job `checks`, com os outros passos condicionados ao evento, ou como job separado. O requisito é só que nada além do audit seja executado.

## Stack Tecnológica

- Ruby on Rails, com Zeitwerk e active_scaffold. As versões não são informadas.
- Gems de checagem: `bundler-audit`, `rubocop`, `brakeman`. As versões não são informadas.
- Bancos: MariaDB no job `test`, SQLite no job `checks`.
- CI: GitHub Actions (premissa 1). Testes com navegador em matriz Chrome + Firefox.
- JS: uma única dependência (codemirror), com `node_modules` versionado.

## Comandos

Os comandos exatos usados hoje no workflow não aparecem na issue. Só os elementos abaixo são conhecidos:

| Passo | O que se sabe | Invocação exata |
|---|---|---|
| Audit | bundle-audit | Desconhecida (igual à atual) |
| Lint | rubocop | Desconhecida (igual à atual) |
| Brakeman | brakeman com `--no-exit-on-warn` | Restante desconhecido |
| Zeitwerk | tarefas `db:schema:load zeitwerk:check`, em SQLite | Prefixo (`bin/rails`, `bundle exec rake` etc.) e variáveis de ambiente desconhecidos |
| Suíte | `Run tests` | Desconhecida |

- Ambiente do job `checks`: `BUNDLE_WITHOUT=production`.
- Build, dev e execução local: Não informado na issue original.

## Estrutura do Projeto

Caminhos citados na issue:

```
Gemfile                 → inclui brakeman (e as gems de audit/lint)
lib/                    → carregado via eager load desde a #680
config/brakeman.ignore  → a criar depois da triagem (fora desta entrega; ver critério 3)
package.json            → única dependência JS: codemirror
node_modules/           → versionado
<arquivo de workflow>   → caminho desconhecido; contém os jobs test, seed, smoke-test
```

## Estilo de Código

Não informado na issue original.

O padrão de referência é o próprio workflow, em que `seed` e `smoke-test` já são jobs separados. O novo job `checks` deve seguir essa forma, com nomes de passo `Audit`, `Lint`, `Brakeman` e `Zeitwerk`.

## Estratégia de Testes

A mudança é de configuração de CI, então a verificação é feita por execuções do workflow:

- **Push com código limpo:** `checks` e cada entrada da matriz `test` aparecem como status independentes e passam. `Audit` e `Lint` aparecem uma única vez.
- **Independência:** com uma ofensa de rubocop deliberada (em branch descartável), `checks` falha e `test` ainda executa `Run tests` e reporta o resultado da suíte.
- **Brakeman em modo relatório:** o passo roda e exibe avisos, mas não reprova `checks` por causa deles.
- **Zeitwerk:** `db:schema:load zeitwerk:check` passa em SQLite. Uma constante com nome incompatível em `lib/`, num teste deliberado, faz o passo falhar.
- **Execução agendada:** um disparo do `schedule` executa só o audit. Nenhum job da matriz nem `seed`/`smoke-test` aparece.

Framework e cobertura da suíte da aplicação: Não informado na issue original (e não mudam com esta entrega).

## Limites

- **Sempre:**
  - manter `checks` e `test` sem dependência (`needs`) entre si;
  - preservar o comportamento atual de `Audit` e `Lint`, mudando só onde rodam;
  - manter `seed` e `smoke-test` intactos nos gatilhos existentes.
- **Perguntar antes:**
  - transformar o Brakeman em portão ou criar/popular `config/brakeman.ignore` (exige triagem do mantenedor);
  - alterar regras de branch protection;
  - mudar gatilhos existentes além de adicionar `schedule`;
  - adicionar gems ou alterar grupos do Gemfile (ex.: se o SQLite não estiver disponível sem `production`).
- **Nunca:**
  - encadear `test` após `checks` (ou o inverso);
  - adicionar MariaDB ou navegador ao `checks`;
  - rodar a suíte, `seed` ou `smoke-test` no gatilho semanal;
  - incluir `yarn audit` ou instalar toolchain JS (fora do escopo, ver abaixo).

## Fora do Escopo

- `yarn audit` para o `package.json`. Há uma única dependência JS (codemirror), o `node_modules` é versionado e o CI não instala yarn. Não compensa montar o toolchain agora.
- Triagem dos avisos existentes do Brakeman e a conversão em portão (etapa posterior).
- Configuração de branch protection no GitHub.

## Critérios de Sucesso

1. Num push, o workflow tem um job `checks` sem `needs`, sem serviço MariaDB e sem navegador, com `BUNDLE_WITHOUT=production`, rodando em paralelo com a matriz `test`.
2. `Audit` e `Lint` executam exatamente uma vez por push, dentro de `checks`, e não aparecem mais em `test`.
3. `Brakeman` executa em `checks` com `--no-exit-on-warn`. Avisos não reprovam o job.
4. `Zeitwerk` executa `db:schema:load zeitwerk:check` em SQLite dentro de `checks` e passa no estado atual do código.
5. Uma falha em `checks` não impede `test` de executar e reportar `Run tests`, e vice-versa.
6. O workflow tem um gatilho `schedule` semanal. Nesse evento, só o audit executa.
7. O job `test` contém apenas os passos necessários à suíte.
8. O comentário "rápido e falha barato" não descreve mais um arranjo inexistente.

## Questões em Aberto

1. **Dia e horário do `schedule`:** qual dia da semana e horário (UTC) usar?
2. **Aviso de falha agendada:** o GitHub notifica por padrão só o último autor do cron. É suficiente ou é preciso outro canal (issue automática, e-mail da equipe etc.)?
3. **Base de vulnerabilidades:** o comando atual de bundle-audit atualiza a base de advisories (ex.: `--update`) antes de checar? No agendamento isso é essencial, já que o objetivo é pegar CVEs novas.
4. **Forma da execução agendada:** preferência entre um job dedicado ao audit e o mesmo job `checks` com passos condicionados ao evento?
5. **SQLite e grupos:** o adaptador SQLite e as gems `brakeman`, `rubocop` e `bundler-audit` estão em grupos instalados com `BUNDLE_WITHOUT=production`?
6. **Ambiente do Zeitwerk:** qual `RAILS_ENV` e qual configuração de banco (`DATABASE_URL` ou `database.yml`) o passo deve usar para apontar para SQLite?
7. **Saída do Brakeman:** basta o log do job, ou o relatório deve ser publicado como artefato ou anotação para facilitar a triagem?
8. **Prazo da triagem:** há prazo ou issue de acompanhamento para tornar o Brakeman um portão?
9. **`workflow_dispatch`:** deve haver disparo manual do audit além do semanal?
10. **Caminho e versões:** qual o caminho do arquivo de workflow e quais as versões de Ruby/Rails usadas no CI? O `checks` deve usar a mesma versão de Ruby que `test`?