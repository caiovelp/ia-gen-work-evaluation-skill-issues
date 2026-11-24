# Spec: Zerar as ofensas do RuboCop e adicioná-lo ao CI

## Objetivo

O `rubocop` está no `Gemfile`, mas nenhum workflow de CI o executa. Por isso o linter pode quebrar sem que ninguém perceba. Isso já aconteceu: depois do bump 1.86.2 → 1.88.2 (#641), `bundle exec rubocop` abortava com `Failed to load plugin`. O motivo foi o `rubocop-rails_config` declarar `rubocop-md` como plugin, e a versão 1.2.4 do `rubocop-md` não implementa o contrato que o 1.88 exige. A suíte `rspec` não detecta esse tipo de falha.

O repositório tinha 411 ofensas em 154 arquivos, o que impedia usar o linter como gate. O ramo atual já levou esse número a zero. Falta transformar o RuboCop em verificação obrigatória do CI, por dois motivos:

1. Impedir que as ofensas voltem.
2. Impedir que o próprio linter quebre de novo em silêncio, seja por bump de gem, plugin incompatível ou configuração inválida.

**Usuários:** os mantenedores e contribuidores do repositório.

**Escopo deste ramo:**
- **Já feito, a validar na revisão:**
  - exclusões de `db/migrate`, `db/schema.rb`, `bin/`, `vendor/` e `node_modules/`;
  - `--autocorrect`;
  - `--autocorrect-all`;
  - conversão de CRLF para LF em 17 arquivos.
- **Proposto:** um job de CI que execute o RuboCop e falhe quando houver ofensas ou erro de execução.

**Fora de escopo:**
- Reformatar migrations antigas.
- Mudar o estilo definido pelo `rubocop-rails_config`.

## Premissas

1. O CI usa GitHub Actions. A issue fala em "workflow", mas não nomeia o provedor.
2. Já existe pelo menos um workflow de testes que roda a suíte em SQLite e em MariaDB.
3. A quebra do plugin (`rubocop-md` 1.2.4 incompatível com `rubocop` 1.88) já foi resolvida neste ramo, já que a contagem chegou a 0 executando o RuboCop. A forma da correção não foi informada.
4. O gate roda sobre o repositório inteiro, e não só sobre o diff. A própria issue considera essa opção viável e mais simples agora que há zero ofensas.
5. A configuração base continua sendo a do `rubocop-rails_config`, com as exclusões listadas acima declaradas no arquivo de configuração do RuboCop do projeto.
6. As ofensas não foram zeradas com `# rubocop:disable` nem com `.rubocop_todo.yml`. Elas foram zeradas por exclusão de diretórios e por correção.
7. Um erro de carregamento de plugin faz `bundle exec rubocop` terminar com código de saída diferente de zero e, portanto, reprova o job.
8. O job de lint roda nos mesmos gatilhos dos testes atuais (push e pull request).

## Stack Tecnológica

- Ruby / Rails. As versões não foram informadas na issue.
- `rubocop` 1.88.2.
- `rubocop-rails_config`, que traz `rubocop-md` como plugin. A versão do `rubocop-md` em uso depois da correção é desconhecida.
- RSpec para a suíte de testes.
- Bancos de teste: SQLite e MariaDB.

## Comandos

```
Lint (gate):                   bundle exec rubocop
Autocorreção segura:           bundle exec rubocop --autocorrect
Autocorreção incl. insegura:   bundle exec rubocop --autocorrect-all
Testes:                        desconhecido (suíte rspec; comando exato e
                               seleção de banco SQLite/MariaDB não informados)
Build / Dev:                   Não informado na issue original.
```

## Estrutura do Projeto

| Caminho | Situação |
|---|---|
| `db/migrate/` | Excluído do RuboCop. São artefatos históricos, e migrations novas saem do gerador do Rails. |
| `db/schema.rb` | Excluído do RuboCop. |
| `bin/` | Excluído do RuboCop. |
| `vendor/` | Excluído do RuboCop. |
| `node_modules/` | Excluído do RuboCop. |
| Arquivo de configuração do RuboCop | Presumivelmente `.rubocop.yml` na raiz (não confirmado). |
| Arquivo(s) de workflow do CI | Caminho e nome desconhecidos. |

## Estilo de Código

O estilo é o definido pelo `rubocop-rails_config`. Na distribuição original das ofensas, os casos mais frequentes eram:

- `Layout/SpaceInsideHashLiteralBraces` (93)
- `Style/FrozenStringLiteralComment` (62)
- `Style/StringLiterals` (58)
- `Layout/TrailingWhitespace` (53)
- `Layout/EndOfLine` (29)

Convenções que esses cops impõem e que agora valem para todo o código fora das exclusões:
- Comentário mágico `# frozen_string_literal: true` no topo dos arquivos Ruby.
- Fim de linha LF. O RuboCop não autocorrige CRLF, então a correção é manual.
- Sem espaço em branco no fim das linhas.
- Aspas e espaçamento de hash conforme o `rubocop-rails_config`.

Não há trecho de código do projeto disponível na issue.

## Estratégia de Testes

- **Regressão funcional da limpeza:** a suíte completa deve passar depois da autocorreção nos dois bancos. Resultado relatado: SQLite com 2263 exemplos e MariaDB com 2303 exemplos, zero falhas em ambos.
- **Risco específico do `--autocorrect-all`:** adicionar `# frozen_string_literal: true` quebra código que muta literais no lugar. Já foi feita uma verificação manual com `grep` por `gsub!`, `sub!`, `concat`, `<<` e similares nos 11 arquivos afetados, sem ocorrências. A suíte verde nos dois bancos é a confirmação complementar.
- **O próprio gate:**
  - um commit com uma ofensa deliberada deve reprovar o job de lint;
  - uma configuração ou plugin que falhe ao carregar também deve reprovar o job.
- Metas de cobertura: Não informado na issue original.

## Limites

- **Sempre:**
  - Manter `bundle exec rubocop` em zero ofensas.
  - Rodar a suíte nos dois bancos depois de qualquer autocorreção.
  - Revisar manualmente as correções inseguras (`--autocorrect-all`) antes de aceitá-las.
- **Perguntar antes:**
  - Adicionar ou remover exclusões.
  - Desativar cops ou criar `.rubocop_todo.yml`.
  - Trocar ou fixar versões de `rubocop`, `rubocop-rails_config` ou `rubocop-md`.
  - Alterar workflows de CI já existentes, além de adicionar o job de lint.
  - Tornar o check obrigatório na proteção de branch.
- **Nunca:**
  - Reformatar migrations já aplicadas.
  - Zerar ofensas com `rubocop:disable` em massa.
  - Fazer o job de lint passar quando o RuboCop termina com erro (por exemplo, com `|| true` ou `continue-on-error`).
  - Remover ou pular testes para acomodar a autocorreção.

## Critérios de Sucesso

1. `bundle exec rubocop`, executado na raiz em um checkout limpo, termina com código 0 e relata 0 ofensas.
2. `bundle exec rubocop` carrega todos os plugins sem erro com as versões travadas no `Gemfile.lock`. Não aparece `Failed to load plugin`.
3. As exclusões `db/migrate`, `db/schema.rb`, `bin/`, `vendor/` e `node_modules/` estão declaradas na configuração do RuboCop, e nenhum arquivo de `db/migrate` foi alterado pela limpeza.
4. Nenhum arquivo Ruby fora das exclusões usa CRLF.
5. A suíte passa com zero falhas em SQLite e em MariaDB.
6. Existe um job de CI que executa `bundle exec rubocop` sobre o repositório inteiro em push e pull request.
7. Esse job falha em dois casos:
   - (a) há pelo menos uma ofensa;
   - (b) o RuboCop não consegue carregar a configuração ou os plugins.

   Isso deve ser demonstrado ao menos uma vez, por exemplo com um commit de teste ou a execução de um PR.
8. Nenhuma ofensa foi suprimida por `rubocop:disable` ou por um arquivo de TODO.

## Perguntas em Aberto

1. **Escopo do gate:** repositório inteiro ou só o diff? A recomendação da issue é o repositório inteiro. Isso precisa de confirmação.
2. **Correção do plugin:** como foi resolvida a incompatibilidade entre `rubocop-md` 1.2.4 e `rubocop` 1.88? Foi um bump do `rubocop-md`, do `rubocop-rails_config`, um pin ou outra solução? Isso deveria ficar registrado.
3. **Bumps automáticos:** há Dependabot ou Renovate? Se houver, o gate deveria ser check obrigatório para que bumps de gems de lint não sejam mesclados com o linter quebrado?
4. **Forma do job:** job novo em workflow próprio ou passo dentro do workflow de testes existente? Qual versão de Ruby e qual estratégia de cache de gems?
5. **Proteção de branch:** o job de lint será check obrigatório para merge?
6. **Regressão de CRLF:** deve-se adicionar um `.gitattributes` (por exemplo, `* text=auto eol=lf`) para evitar que CRLF volte, já que o RuboCop não o autocorrige?
7. **Exclusão de `bin/`:** é intencional excluir também binstubs editados à mão, ou só os gerados?
8. **Migrations novas:** devem continuar excluídas mesmo quando criadas depois deste ramo? A issue sugere que sim, porque saem do gerador do Rails.
9. **Comando de testes:** qual é o comando exato do CI para rodar a suíte em SQLite e em MariaDB? Não consta na issue.