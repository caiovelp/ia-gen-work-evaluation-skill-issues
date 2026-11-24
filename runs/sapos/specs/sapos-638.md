# Spec: Atualização do `jquery-ui-rails` (7.0.0 → 8.0.0) e avaliação de saída da jQuery UI

## Objetivo

Tirar o `jquery-ui-rails` dos alertas do `bundle-audit` sem quebrar as telas do SAPOS. Hoje o `Gemfile` fixa a 7.0.0, que traz a jQuery UI 1.13.0. A 8.0.0 traz a 1.14.x, e o caminho até ela não é um simples bump de `Gemfile.lock`.

**Contexto da vulnerabilidade (registro, não motivação principal):**
- A GHSA-h6gj-6jjq-h8g9 / CVE-2022-31160 afeta a série 1.13 e foi corrigida na 1.13.2.
- O widget afetado é o `checkboxradio`.
- Um `grep` por `checkboxradio` em `app/`, `lib/`, `vendor/` e `config/` não retorna nada. O código do SAPOS não usa o widget.
- Esse registro existe para que o tema não volte à mesa a cada rodada de auditoria.

**Problema real:**
- A lib aparece no `bundle-audit`.
- A 8.0.0 reestrutura os caminhos de assets. Com ela, os pontos de entrada atuais deixam de existir, o `application.css` não compila e as telas retornam 500.
- No teste de bump, quatro request specs de Devise quebraram por esse motivo.

**Encaminhamentos em avaliação (descritos na issue):**
1. **Subir para a 8.0.0.** Reescrever os imports de asset para o layout da jQuery UI 1.14 e validar as telas em homologação. Exige menor esforço e mantém a arquitetura atual.
2. **Importar só os módulos usados** em vez do bundle inteiro (`//= require jquery-ui`). Reduz a superfície exposta e pode ser feito junto com a opção 1.
3. **Sair da jQuery UI.** Substituir datepicker e autocomplete (por exemplo, pelo `<input type="date">` nativo ou por um componente dedicado) e resolver o que o `active_scaffold` espera encontrar. Só faz sentido em conjunto com a #621, provavelmente depois dela.

**Usuários afetados:** usuários das telas do SAPOS que usam datepicker, autocomplete e as telas geradas pelo `active_scaffold`. Os fluxos de autenticação Devise também são afetados, porque quebram quando o CSS não compila.

**Escopo proposto desta spec:** opção 1, opcionalmente com a opção 2. A opção 3 fica fora de escopo e vinculada à #621 (ver Premissas e Perguntas em Aberto).

## Premissas

1. O alvo desta issue é a opção 1, com a opção 2 se couber. A saída completa da jQuery UI (opção 3) será tratada depois ou junto com a #621.
2. Os únicos widgets da jQuery UI usados pelo código próprio do SAPOS são **datepicker** e **autocomplete**. Essa conclusão veio de leitura de código e ainda não foi confirmada pelo uso real.
3. O `active_scaffold` 4.0.13 continuará instalado durante esta mudança. Seu acoplamento com a jQuery UI precisa continuar funcionando:
   - `app/assets/stylesheets/active_scaffold_jquery_ui.css.erb` faz `require_asset 'jquery-ui'`;
   - o mesmo arquivo ramifica pela constante `Jquery::Ui::Rails::VERSION`;
   - `lib/active_scaffold/bridges/date_picker.rb` dirige o `$.datepicker`.
4. Os quatro request specs de Devise que quebraram no bump servem como indicador mínimo de regressão de compilação de assets.
5. O CVE-2022-31160 é considerado não explorável no SAPOS, porque o `checkboxradio` não é usado. Esta mudança não é tratada como correção de segurança urgente.
6. A versão 8.0.0 do gem resolve o alerta do `bundle-audit`, já que traz a jQuery UI 1.14.x, posterior à 1.13.2.

## Stack Técnica

- Ruby on Rails com asset pipeline (Sprockets, inferido pelo uso de `//= require` e `require_asset`). Versões de Ruby e Rails: não informado na issue original.
- `jquery-ui-rails`: 7.0.0 hoje (jQuery UI 1.13.0), com alvo 8.0.0 (jQuery UI 1.14.x).
- `active_scaffold`: 4.0.13.
- Devise, inferido pelos request specs citados.
- SCSS (`application.css.scss`).
- `bundle-audit` para auditoria de dependências.
- Versão do jQuery base: não informado na issue original.

## Comandos

Não informado na issue original.

A issue menciona `bundle-audit`, `grep` e a execução de request specs, mas não traz os comandos exatos. Os comandos de build, teste, lint, dev e auditoria são desconhecidos.

## Estrutura do Projeto

Caminhos citados na issue:

```
Gemfile                                        → fixa jquery-ui-rails em 7.0.0
app/assets/javascripts/application.js          → //= require jquery-ui (bundle inteiro)
app/assets/stylesheets/application.css.scss    → @import "jquery-ui.css"
                                                  @import "jquery-ui/datepicker.css"
app/, lib/, vendor/, config/                   → diretórios varridos no grep por checkboxradio
```

Caminhos **dentro do gem `active_scaffold`** (não no repositório do SAPOS):

```
app/assets/stylesheets/active_scaffold_jquery_ui.css.erb   (4.0.13)
lib/active_scaffold/bridges/date_picker.rb                 (4.0.13 e master)
lib/active_scaffold/assets/jquery_ui_manifest.rb           (master)
lib/active_scaffold/assets/jquery_ui_theme_generator.rb    (master)
```

Localização dos request specs de Devise: não informado na issue original.

## Estilo de Código

Não informado na issue original.

Como referência do estado atual, estes são os imports existentes que precisam ser reescritos:

```js
// app/assets/javascripts/application.js
//= require jquery-ui
```

```scss
// app/assets/stylesheets/application.css.scss
@import "jquery-ui.css";
@import "jquery-ui/datepicker.css";
```

Os novos caminhos de asset da 8.0.0 / jQuery UI 1.14 não são informados na issue. Eles precisam ser levantados na documentação ou no conteúdo do gem.

## Estratégia de Testes

- **Request specs:** os quatro request specs de Devise que quebraram no bump precisam passar. Os demais request specs também precisam continuar passando. Framework (RSpec ou outro) e localização: não informado na issue original.
- **Compilação de assets:** o `application.css` e o `application.js` precisam compilar sem erro com a 8.0.0. O comando de pré-compilação não é informado na issue.
- **Validação manual em homologação:** telas com datepicker, telas com autocomplete e telas do `active_scaffold`, incluindo o date picker via ponte `bridges/date_picker.rb` e o CSS de tema `active_scaffold_jquery_ui.css.erb`.
- **Auditoria:** o `bundle-audit` não deve mais apontar o `jquery-ui-rails`.
- Testes de sistema/JS automatizados para datepicker e autocomplete: não informado na issue se existem.
- Metas de cobertura: não informado na issue original.

## Limites

- **Sempre:**
  - Validar em homologação as telas que usam jQuery UI antes de considerar a mudança concluída.
  - Rodar os request specs, em especial os de Devise, após qualquer alteração de imports de asset.
  - Confirmar a compilação do CSS e do JS.
- **Perguntar antes:**
  - Remover a jQuery UI por completo (opção 3).
  - Atualizar ou alterar a integração do `active_scaffold` (escopo da #621).
  - Fixar versão de gem diferente da 8.0.0.
  - Adicionar nova dependência de datepicker/autocomplete.
  - Restringir os módulos importados (opção 2), se houver risco de quebrar o que o `active_scaffold` espera via `require_asset 'jquery-ui'`.
- **Nunca:**
  - Fazer só o bump de `Gemfile.lock` sem reescrever os imports.
  - Editar arquivos internos do gem `active_scaffold` para contornar a quebra.
  - Remover ou pular os request specs que falham sem aprovação.
  - Silenciar o alerta do `bundle-audit` (por exemplo, por ignore) como substituto da atualização sem decisão explícita.

## Critérios de Sucesso

1. O `Gemfile` / `Gemfile.lock` referenciam `jquery-ui-rails` 8.0.0, com jQuery UI 1.14.x.
2. Os imports em `application.js` e `application.css.scss` usam os caminhos válidos da jQuery UI 1.14. Não restam referências a `jquery-ui.css` nem a `jquery-ui/datepicker.css` no layout antigo, a menos que continuem válidas na 8.0.0.
3. O `application.css` compila e nenhuma tela retorna 500 por erro de asset.
4. Os quatro request specs de Devise que quebraram no bump passam, e a suíte de request specs fica verde.
5. Em homologação, datepicker e autocomplete funcionam nas telas próprias do SAPOS, incluindo comportamento e aparência (CSS do tema).
6. Em homologação, as telas do `active_scaffold` funcionam:
   - o date picker abre e grava data corretamente;
   - o CSS `active_scaffold_jquery_ui.css.erb` resolve corretamente com `Jquery::Ui::Rails::VERSION` em 8.x.
7. O `bundle-audit` não lista mais o `jquery-ui-rails`.
8. Se a opção 2 for adotada, o `application.js` importa apenas os módulos de datepicker e autocomplete, mais as dependências internas da jQuery UI que eles exigirem, e os critérios 3 a 6 continuam válidos.
9. A decisão sobre a opção 3 fica registrada, seja na issue, na #621 ou na spec, junto com a nota de que o CVE-2022-31160 não se aplica (`checkboxradio` não é usado).

## Perguntas em Aberto

1. **Escopo:** a opção 3 (sair da jQuery UI) é ambição real desta issue, ou o alvo é a opção 1, deixando a lib para trás só quando o `active_scaffold` sair (#621)? A resposta define se a issue é pequena ou grande.
2. **Widgets em uso:** alguma tela em uso depende de widget da jQuery UI além de datepicker e autocomplete? O levantamento foi feito por leitura de código. Quais funcionalidades estão de fato em uso em produção?
3. **Compatibilidade do `active_scaffold` 4.0.13 com a 8.0.0:**
   - O `require_asset 'jquery-ui'` em `active_scaffold_jquery_ui.css.erb` continua resolvendo no novo layout de assets?
   - O ramo selecionado por `Jquery::Ui::Rails::VERSION` trata versões 8.x?
   - Se não, a atualização depende da #621?
4. **Opção 2 e o `active_scaffold`:** importar só os módulos usados é compatível com o `active_scaffold`, que pede o bundle `jquery-ui` por conta própria? Na prática, o bundle inteiro continuaria sendo carregado por essa via?
5. **jQuery base:** qual versão do jQuery o SAPOS usa, e ela é compatível com a jQuery UI 1.14?
6. **Versão da jQuery UI no gem:** qual 1.14.x exatamente a `jquery-ui-rails` 8.0.0 empacota? Há expectativa de versão do gem com a 1.14.2 (28/01/2026), ou a 8.0.0 basta?
7. **Telas de homologação:** existe uma lista ou roteiro das telas a validar? Quem faz a validação?
8. **Testes automatizados de JS:** existem testes de sistema/feature cobrindo datepicker e autocomplete, ou a validação será só manual?
9. **Comandos:** quais são os comandos do projeto para rodar a suíte de testes, pré-compilar assets e executar o `bundle-audit`?