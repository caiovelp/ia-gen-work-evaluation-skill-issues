# Especificação: Atualização do Rails da série 7.2 para a 8.x

## Objetivo

Migrar o projeto do **Rails 7.2.3.1** para a série **8.x**. A série 7.2 recebe apenas correções de segurança e tem prazo de suporte. Uma série com manutenção ativa reduz o risco de ficar sem correções.

A issue reúne o que já foi medido no código, para que a migração não comece do zero.

**Quem se beneficia:** a equipe de manutenção do projeto. Os usuários finais não devem perceber mudança de comportamento, como relatórios PDF/XLSX, telas do active_scaffold ou consultas somente leitura.

**Escopo descrito na issue, na ordem sugerida:**

1. Trocar o `enum` com argumentos nomeados pela forma posicional em `app/models/report_configuration.rb:21`. A troca pode ser feita antes do salto.
2. Concluir a #636, que cria testes de caracterização para PDF/XLSX.
3. Resolver a #621, que atualiza o active_scaffold.
4. Subir o `rack` para a série 3, junto com `rack-session` e `rackup`.
5. Subir o Rails para 8.x e revisar um a um os cinco monkey-patches de `config/initializers/`.
6. Fazer uma homologação comparativa num ambiente equivalente ao de produção (MariaDB).

**Fora do escopo desta especificação:** o conteúdo das issues #621, #636 e #638. Elas são dependências e têm especificação própria. A atualização do Ruby também fica de fora, porque a #639 já a trata.

## Premissas

1. O alvo é a última versão estável da série 8.x disponível no início do trabalho. A issue não diz se é 8.0 ou 8.1.
2. A série 3.4 do Ruby (#639) já está em uso, ou estará antes do passo 5. A issue afirma que ela atende o Rails 8, que exige Ruby >= 3.2.
3. A suíte de testes usa RSpec (`rspec-rails`, `shoulda-matchers`) e roda em SQLite. Essa suíte, com 2246 exemplos, é a linha de base de comportamento.
4. Produção usa MariaDB com collation `utf8mb4_unicode_ci` e `STRICT_TRANS_TABLES`. Existe, ou é possível criar, um ambiente de homologação com a mesma configuração.
5. A única deprecation emitida hoje é a do `enum` citada na issue. Ela foi medida na suíte completa, não em produção.
6. O `grep` por `enum <nome>:` em `app/models/` é suficiente para garantir que não há outras ocorrências do padrão antigo. Fora de `app/models/`, isso não foi verificado.
7. As dependências #621 e #636 serão concluídas antes do salto de major, como a própria issue recomenda. A #638 não bloqueia.
8. Cada passo da ordem sugerida será entregue em PR separado. A issue não diz isso explicitamente.

## Stack Tecnológica

| Componente | Atual | Alvo |
|---|---|---|
| Ruby | série 3.4 (via #639) | série 3.4 (sem mudança) |
| Rails | 7.2.3.1 | 8.x (versão exata em aberto) |
| rack | `~> 2.2.23` | série 3 |
| rack-session | 1.0.x | 2.x |
| rackup | 1.0.x | 2.x |
| active_scaffold | `~> 4.0.13` | versão definida pela #621 (4.3.1 publicada) |
| recordselect | Não informado na issue original. | Não informado na issue original. |
| rspec-rails | 7.1.1 | 8.0.4 |
| shoulda-matchers | 7.0.1 | 8.0.1 |
| rails-erd | 1.7.2 | 2.1.0 |
| jquery-ui-rails | Não informado na issue original (ver #638). | Não informado na issue original. |
| Banco nos testes | SQLite | SQLite |
| Banco em produção | MariaDB (`utf8mb4_unicode_ci`, `STRICT_TRANS_TABLES`), cliente `Mysql2` | sem mudança |

## Comandos

- **Testes:** Não informado na issue original. A issue cita a "suíte inteira (2246 exemplos)" e o uso de `rspec-rails`, mas não mostra o comando exato.
- **Verificar gems desatualizadas:** `bundle outdated`, citado na issue. Flags não informadas.
- **Build, lint e dev:** Não informado na issue original.
- **Capturar deprecations:** Não informado na issue original. A issue não diz como a deprecation foi coletada, por exemplo com qual configuração de `ActiveSupport::Deprecation` ou de log.
- **Implantação em homologação:** Não informado na issue original.

## Estrutura do Projeto

Apenas os caminhos citados na issue:

```
app/models/report_configuration.rb          → contém o enum com a forma deprecada (linha 21)
app/models/                                 → escopo do grep por outros enums
config/initializers/                        → os cinco monkey-patches:
  fix_rails7_date_format.rb
  fix_url_for.rb
  fix_rails61_active_scaffold_dependent_error.rb
  recordselect_patch.rb                     → reabre AbstractMysqlAdapter
  active_scaffold_disable_null_comparators.rb
db/seeds/02.reports_notifications.rb        → bloco que só carrega em MySQL
Gemfile                                     → travas de rack e active_scaffold
AGENTS.md                                   → lista o código que a suíte não executa
```

O código de `Query.run_read_only_query` está num arquivo que a issue não informa. A localização dos testes também não foi informada.

## Estilo de Código

Não há um guia de estilo na issue. O único padrão de código explícito é a forma de declarar `enum`, que passa a ser obrigatória:

```ruby
# Forma deprecada (removida no Rails 8.0), não usar:
enum signature_type: { no_signature: 0, manual: 1, qr_code: 2 }

# Forma posicional, a ser usada:
enum :signature_type, { no_signature: 0, manual: 1, qr_code: 2 }
```

Demais convenções de nomes e formatação: Não informado na issue original.

## Estratégia de Testes

- **Linha de base:** a suíte RSpec atual, com 2246 exemplos, rodando em SQLite. Antes de cada passo, ela deve estar verde e emitir no máximo a deprecation conhecida.
- **Caracterização de PDF/XLSX:** depende da #636. Hoje a suíte só confere o nome do arquivo baixado, o que não basta para detectar regressões de renderização num salto de major. A #636 deve estar concluída antes do passo 5.
- **Atualização do active_scaffold:** a #621 já prevê saltos sucessivos de versão, cada um com teste e correção.
- **O que a suíte não cobre e só a homologação alcança:**
  - `recordselect_patch.rb`, que reabre `AbstractMysqlAdapter`. Como a suíte roda em SQLite, uma suíte verde nada diz sobre ele.
  - `Query.run_read_only_query`, que ramifica por adaptador e abre um cliente `Mysql2` próprio.
  - O bloco exclusivo de MySQL em `db/seeds/02.reports_notifications.rb`.
  - O comportamento sob a collation `utf8mb4_unicode_ci` e o modo `STRICT_TRANS_TABLES`.
- **Homologação comparativa:** mesmos fluxos executados na versão atual (7.2) e na nova (8.x), em ambiente MariaDB. O roteiro e os critérios de comparação estão em aberto.
- **Cobertura mínima exigida:** Não informado na issue original.

## Limites

- **Sempre:**
  - Rodar a suíte completa a cada passo e conferir a lista de deprecations emitidas.
  - Revisar cada monkey-patch individualmente e registrar a decisão: remover, adaptar ou manter, com justificativa.
  - Seguir a ordem de dependências: #636 e #621 antes do salto de major.
  - Subir junto as gems companheiras amarradas ao major do Rails: `rspec-rails`, `shoulda-matchers` e `rails-erd`.
- **Perguntar antes:**
  - Remover qualquer monkey-patch de `config/initializers/`.
  - Escolher a versão-alvo exata (8.0 ou 8.1).
  - Atualizar gems além das citadas na issue.
  - Mudar o comportamento de `Query.run_read_only_query` ou dos seeds.
  - Iniciar o salto de major sem a #636 ou a #621 concluídas.
- **Nunca:**
  - Considerar o `recordselect_patch.rb`, o `Query.run_read_only_query` ou o seed exclusivo de MySQL validados só porque a suíte em SQLite está verde.
  - Remover ou desativar testes que falharem durante a migração sem aprovação.
  - Promover para produção sem a homologação comparativa em MariaDB.

## Critérios de Sucesso

1. `app/models/report_configuration.rb` usa a forma posicional do `enum`, e a suíte completa no Rails 7.2 roda sem nenhuma deprecation.
2. O `Gemfile` e o `Gemfile.lock` apontam para Rails 8.x, `rack` 3.x, `rack-session` 2.x e `rackup` 2.x, com `bundle install` concluído sem conflito.
3. `rspec-rails`, `shoulda-matchers` e `rails-erd` estão nas versões compatíveis com o Rails 8 (8.0.x, 8.0.x e 2.x, respectivamente, ou superiores).
4. O active_scaffold está numa versão compatível com o Rails 8, conforme a resolução da #621.
5. A suíte completa, com pelo menos 2246 exemplos e somada aos testes de caracterização da #636, passa no Rails 8.x sem falhas e sem deprecations.
6. Cada um dos cinco monkey-patches tem decisão documentada (removido, adaptado ou mantido) com justificativa. Os que forem mantidos funcionam no Rails 8.x.
7. A homologação comparativa em MariaDB (`utf8mb4_unicode_ci`, `STRICT_TRANS_TABLES`) confirma comportamento equivalente ao da 7.2 em, no mínimo:
   - consultas que passam pelo `recordselect_patch.rb`;
   - `Query.run_read_only_query`;
   - carga de `db/seeds/02.reports_notifications.rb`;
   - geração de relatórios PDF e XLSX.
8. A data de fim de suporte da série 7.2 foi confirmada na política de manutenção oficial e registrada, e o cronograma termina antes dela.

## Perguntas em Aberto

1. **Versão-alvo:** 8.0 ou a versão mais recente da série 8.x (por exemplo 8.1)? A escolha muda a lista de deprecations e de breaking changes a revisar.
2. **Prazo:** qual é a data exata de fim de suporte de segurança da 7.2? A issue pede que isso seja confirmado na política de manutenção antes de montar o cronograma.
3. **Rack 3 é mesmo obrigatório?** A issue afirma que o Rails 8 pede `rack` 3. É preciso confirmar isso no gemspec da versão-alvo. Se o Rails 8.0 ainda aceitar `rack` 2.2, o passo 4 pode virar etapa independente em vez de pré-requisito. Também falta saber o que mais no projeto depende de `rack` 2, como middlewares e outras gems.
4. **active_scaffold e recordselect:** qual versão mínima do active_scaffold suporta Rails 8, e ela coincide com o ponto de chegada da #621 (4.3.1 ou outra)? Qual versão do recordselect acompanha?
5. **Monkey-patches:** há registro de por que cada um foi criado, como issue, commit ou bug upstream? Sem isso, fica difícil decidir se ainda são necessários. Em especial, `fix_rails61_active_scaffold_dependent_error.rb` e `fix_rails7_date_format.rb` podem já ter sido resolvidos upstream.
6. **Homologação:** existe um ambiente MariaDB de homologação disponível? Existe um roteiro de fluxos a comparar? Quem executa e aprova?
7. **Cobertura de MySQL/MariaDB:** convém rodar a suíte, ou parte dela, também contra MariaDB em CI, em vez de depender só da homologação manual? Fazer isso amplia o escopo.
8. **Escopo da busca por deprecations:** o `grep` cobriu só `app/models/`. É preciso verificar também `lib/`, concerns e engines? A medição de deprecations considerou código que a suíte não exercita?
9. **#638 (jquery-ui-rails):** mesmo sem bloquear, deve ser tratada antes, durante ou depois deste salto, dado o acoplamento com assets e com o active_scaffold?
10. **Estrutura da entrega:** esta issue junta várias entregas que podem ser testadas de forma independente (enum, rack, Rails, monkey-patches, homologação). Convém quebrá-la em sub-issues, uma por passo, para revisar e reverter separadamente?
11. **Comandos e infraestrutura:** quais são os comandos oficiais de teste, lint e build, e qual é a configuração de CI? Nenhum deles aparece na issue.