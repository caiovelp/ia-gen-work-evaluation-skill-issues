# Spec: Atualizar gems atrasadas em minor e alinhar as restrições do Gemfile

## Objetivo

Trazer o bundle para as versões minor mais recentes dentro da major atual e deixar cada restrição do `Gemfile` de acordo com o critério da skill `dependencias`. A mudança tem dois escopos independentes.

**Escopo 1: atualizar as gems atrasadas em minor**

- O `bundle outdated --strict` aponta 37 gems atrasadas em minor. Todas devem ir para a versão minor mais recente sem cruzar nenhuma major.
  - Runtime (20): `active_scaffold_duplicate`, `activerecord-session_store`, `caxlsx`, `caxlsx_rails`, `et-orbi`, `exception_notification`, `execjs`, `fugit`, `globalid`, `i18n`, `json`, `liquid`, `prawn-rails`, `psych`, `raabro`, `recaptcha`, `rubyzip`, `simple-navigation`, `tilt`, `tzinfo-data`.
  - Dev/test (16, segundo a issue): família `rubocop` (6), `pry`, `selenium-webdriver`, `factory_bot`, `launchy`, `rouge`, `simplecov-html`, `database_cleaner-core`, `binding_of_caller`, `debug_inspector`.
- O `ostruct` deve sair do `Gemfile.lock`. Ele era dependência do `simple-navigation` 4.4.1, e a 4.5.0 não precisa mais dele.
- Gems de maior risco, que exigem atenção específica:
  - Gems 0.x, em que um minor pode quebrar o contrato: `caxlsx_rails` (0.6.4 → 0.7.2, a única de runtime), `pry`, `rubocop-minitest`, `rubocop-packaging`, `simplecov-html`.
  - Gems no ponto cego da #636: `caxlsx_rails`, `prawn-rails` e `liquid`. Os feature specs de PDF/XLSX verificam só o nome do arquivo baixado. São 13 views `.pdf.prawn` e 1 `.xlsx.axlsx`. Por isso, suíte verde não prova que a saída continua igual.

**Escopo 2: alinhar as restrições do Gemfile ao critério**

O critério é este: com `Gemfile.lock` versionado, uma restrição expressa política, não reprodutibilidade. A gem é declarada só pelo nome, a não ser que um bump exija migração. Quando há restrição, ela cobre exatamente o motivo, e o motivo fica escrito ao lado.

| gem | restrição atual | ação |
|---|---|---|
| `rails` | `~> 7.2.3`, `>= 7.2.3.1` | mantém (minor de Rails exige migração; o piso é de segurança). O motivo precisa estar escrito |
| `rack` | `~> 2.2.23` | mantém (major com quebra real, ligada ao salto do Rails) |
| `active_scaffold` | `~> 4.0.13` | mantém; o comentário passa a apontar a #621 |
| `jquery-ui-rails` | `~> 7.0.0` | mantém; o comentário passa a apontar a #638 |
| `nokogiri` | `>= 1.18.9` | sem alteração (modelo da forma) |
| `carrierwave` | `>= 3.0.7` | mantém; o comentário passa a dizer que é piso de segurança (#450) |
| `devise` | `~> 5.0`, `>= 5.0.4` | mantém; o motivo passa a ser escrito |
| `puma` | `~> 7.2`, `>= 7.2.1` | **pendente da decisão do mantenedor** |
| `devise_invitable` | `~> 2.0.0` | **remover a restrição** (pin incidental do commit `128e03e2`, #373) |
| `active_scaffold_duplicate` | `>= 1.1.0` | **remover a restrição** (piso sem motivo, do mesmo commit) |
| `validates_timeliness` | `~> 7.1.0` | passa a `~> 7`, com o motivo escrito |
| `sqlite3` | `~> 2.9.5` | passa a `>= 2.9.5` (o motivo declarado é piso de CVE) |

**Usuário:** mantenedores da aplicação.

**Sucesso:** o lock fica atualizado em minor, cada restrição do Gemfile tem um motivo escrito e proporcional, e nenhuma regressão aparece, inclusive na saída de PDF/XLSX e na ordenação com collation.

## Premissas

1. A suíte citada ("2243 exemplos, 0 falhas, 9m36s") é a suíte completa do projeto, e o resultado da sondagem `bundle update --minor --strict` vale como linha de base.
2. O lock final do Escopo 1 será igual ao produzido pela sondagem, ou seja, nenhuma gem fora da lista muda de versão.
3. Mudar restrições no Escopo 2 não deve alterar o `Gemfile.lock` além do que o Escopo 1 já alterou. Afrouxar `sqlite3`, `validates_timeliness`, `devise_invitable` e `active_scaffold_duplicate` não autoriza subir major neste trabalho.
4. O formato do comentário de motivo segue o modelo já usado em `nokogiri`, cujo texto exato não aparece na issue.
5. `active_scaffold_duplicate` aparece nos dois escopos. A gem sobe no Escopo 1, e o piso `>= 1.1.0` sai no Escopo 2.
6. A ordem sugerida, com a #636 antes de fechar o Escopo 1, é recomendação e não bloqueio rígido. Até a #636 existir, a validação de PDF/XLSX é manual.
7. Os dois escopos podem ser revisados separadamente, mas entram na mesma issue.

## Stack técnica

- Ruby / Bundler, com `Gemfile.lock` versionado.
- Rails 7.2.3.x, rack 2.2.x, active_scaffold 4.0.13, devise 5.x, puma 7.2.x (só em desenvolvimento, a confirmar). Produção roda em Apache + Passenger.
- Banco na suíte: SQLite (`sqlite3` 2.9.5+). Há ainda uma variante MariaDB executada pela skill `suite-mariadb`.
- Geração de relatórios: `prawn-rails` (views `.pdf.prawn`), `caxlsx` / `caxlsx_rails` (views `.xlsx.axlsx`), `liquid`.
- Versão de Ruby e demais versões: não informadas na issue original.

## Comandos

```
Gems atrasadas:     bundle outdated --strict
Atualização minor:  bundle update --minor --strict
Auditoria de CVE:   bundle audit
Suíte (SQLite):     desconhecido, não informado na issue
Suíte (MariaDB):    via skill `suite-mariadb`, comando concreto desconhecido
Lint (rubocop):     desconhecido, não informado na issue
```

## Estrutura do projeto

```
Gemfile          → declarações e restrições (alvo do Escopo 2)
Gemfile.lock     → versionado (alvo do Escopo 1)
*.pdf.prawn      → 13 views de PDF (caminho desconhecido)
*.xlsx.axlsx     → 1 view de XLSX (caminho desconhecido)
feature specs    → cobrem download de PDF/XLSX só pelo nome do arquivo (caminho desconhecido)
```

Os demais caminhos não foram informados na issue original.

## Estilo de código

- Cada restrição no `Gemfile` leva ao lado um comentário com o motivo e, quando houver, a issue de referência (#621, #638, #450).
- A restrição cobre exatamente o motivo:
  - piso de segurança → `>=`
  - bloqueio de major → `~> N`
  - granularidade de patch só quando o motivo exigir
- O modelo da forma é a declaração do `nokogiri`. O texto exato dessa linha não aparece na issue.

## Estratégia de testes

- Rodar a suíte completa em SQLite após o Escopo 1 e após o Escopo 2. A referência é 2243 exemplos e 0 falhas.
- Repetir a suíte com a skill `suite-mariadb`, por causa da ordenação de nomes acentuados, que depende de collation.
- Validar manualmente as 13 views `.pdf.prawn` e a view `.xlsx.axlsx`, comparando a saída antes e depois do bump de `caxlsx_rails`, `prawn-rails` e `liquid`. Essa validação vale até a #636 automatizar a verificação de conteúdo.
- Rodar `bundle audit`. Nenhuma CVE nova é aceitável além da pendência já registrada na #638.
- Rodar o rubocop após o bump da família `rubocop`, já que novas regras podem gerar ofensas.
- Exercitar as ferramentas 0.x de dev (`pry`, `simplecov-html`) no uso real: console e relatório de cobertura.
- Nível e cobertura exigidos: não informados na issue original.

## Limites

- **Sempre:**
  - manter cada gem dentro da major atual;
  - escrever o motivo ao lado de toda restrição mantida ou criada;
  - rodar a suíte em SQLite e em MariaDB;
  - rodar `bundle audit`.
- **Perguntar antes:**
  - alterar a restrição do `puma`;
  - qualquer bump que cruze major;
  - qualquer gem fora da lista que mude de versão no lock;
  - aceitar diferença visível na saída de PDF/XLSX.
- **Nunca:**
  - subir `active_scaffold` (#621), `jquery-ui-rails` (#638) ou Rails 8.x neste trabalho;
  - implementar aqui a cobertura de conteúdo da #636;
  - remover ou afrouxar pisos de segurança (`rails`, `carrierwave`, `nokogiri`, `sqlite3`, `devise`).

## Critérios de sucesso

1. `bundle outdated --strict` não aponta nenhuma gem atrasada em minor, exceto as excluídas por restrição deliberada e documentada.
2. Nenhuma gem cruzou major. O diff do `Gemfile.lock` contém só as gems listadas, as dependências transitivas delas e a remoção do `ostruct`.
3. `ostruct` não aparece mais no `Gemfile.lock`.
4. A suíte em SQLite passa com 0 falhas e pelo menos 2243 exemplos.
5. A suíte via `suite-mariadb` passa com 0 falhas.
6. `bundle audit` não aponta nenhuma CVE além da já registrada na #638.
7. As 13 saídas PDF e a saída XLSX foram conferidas e são equivalentes às de antes do bump. Isso vale pela validação manual ou pela #636, se ela for concluída antes.
8. As restrições no `Gemfile` estão assim:
   - `devise_invitable` e `active_scaffold_duplicate` declarados só pelo nome;
   - `validates_timeliness` como `~> 7`;
   - `sqlite3` como `>= 2.9.5`;
   - cada restrição restante com motivo escrito ao lado, incluindo as referências #621 (`active_scaffold`), #638 (`jquery-ui-rails`) e #450 (`carrierwave`), além dos motivos de `devise` e `rails`.
9. O `puma` segue a decisão registrada do mantenedor.
10. O rubocop não acusa ofensas novas, ou as novas foram tratadas.

## Perguntas em aberto

1. **puma:** a produção roda só em Apache + Passenger, e o puma serve apenas ao desenvolvimento? Se sim, a restrição `~> 7.2` continua ou passa a declaração só pelo nome, ou com piso, liberando o 8.x?
2. **Contagem:** a issue fala em 37 gems atrasadas, mas as listas somam 20 + 16 = 36. Além disso, a lista de dev/test nomeia 6 + 9 = 15 itens, não 16. Qual gem falta?
3. **Família rubocop:** quais são as 6 gems? Só `rubocop-minitest` e `rubocop-packaging` foram nomeadas.
4. **Motivo do `validates_timeliness`:** qual é o motivo da restrição a ser escrito no comentário? A issue diz só que `~> 7` "diria o mesmo".
5. **Motivo do `devise`:** qual é o texto da "precaução legítima"? O piso `>= 5.0.4` é de segurança?
6. **Ordem com a #636:** concluir a #636 antes de fechar o Escopo 1 é obrigatório, ou basta a validação manual de PDF/XLSX?
7. **Forma de entrega:** os dois escopos vão em um único PR ou em PRs separados?
8. **Afrouxamento do `sqlite3`:** com `>= 2.9.5` deixa de haver teto de major. Isso é aceitável como política, ou convém `~> 2.9, >= 2.9.5`?
9. **Afrouxamento do `devise_invitable`:** remover o pin libera uma futura 3.x. Isso é aceitável sem restrição de major?
10. **Validação manual:** qual procedimento usar para comparar a saída de PDF/XLSX? Por exemplo, diff de texto extraído, conferência visual, ou dados de referência para os relatórios.
11. **Comandos:** quais são os comandos concretos da suíte, do lint e da skill `suite-mariadb`?