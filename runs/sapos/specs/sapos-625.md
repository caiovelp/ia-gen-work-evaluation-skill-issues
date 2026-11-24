# Spec: Aposentar o monkey-patch de `Date#to_s` (`fix_rails7_date_format.rb`)

## Objetivo

Remover o initializer `config/initializers/fix_rails7_date_format.rb`. Ele sobrescreve `Date#to_s` globalmente para que a interpolação de datas use o formato `:default` (`%d/%m/%Y`). Os pontos que dependem desse comportamento implícito passam a pedir o formato de forma explícita, com `to_fs(:default)` ou com a localização do I18n (`l`).

**Por quê:**
- O patch já quebrou no upgrade para o Rails 7.2. O fallback chamava `to_default_s`, um método interno que foi removido, e `Date#to_s(:formato_desconhecido)` passou a levantar `NameError`. Nenhum spec cobria esse caminho. A falha foi corrigida em separado, já com specs.
- O patch sobrescreve um método do núcleo do Ruby, globalmente, com aridade diferente da original. O `Date#to_s` original não aceita argumento.
- O Rails removeu esse comportamento de propósito e oferece `to_fs(format)` no lugar.
- O projeto já convive com esse modelo para `Time`. `Time::DATE_FORMATS[:default]` está configurado em `config/initializers/datetime.rb` sem patch equivalente. `Time#to_s` devolve ISO, e o código chama `to_fs` onde precisa do formato brasileiro, como em `lib/notifier.rb`.

**Usuários afetados:** todos que veem datas renderizadas pela aplicação, em views, PDFs, planilhas, notificações e telas do active_scaffold. Também os desenvolvedores, que deixam de depender de um comportamento global implícito.

**Critério de aceitação em alto nível:** depois da remoção do patch, toda data exibida ao usuário mantém o formato que tinha antes (`dd/mm/aaaa`), salvo mudanças aprovadas explicitamente. Todo uso indireto de `Date#to_s`, como `to_param`, URLs e interpolações, foi auditado e tem o comportamento novo (ISO) aceito ou tratado.

## Premissas

1. A demanda é uma única capacidade (remover o patch e migrar os usos). Não é preciso um mapa de capacidades.
2. O formato `:default` de `Date` (`%d/%m/%Y`) continua configurado em `Date::DATE_FORMATS` depois da remoção, porque `to_fs(:default)` depende dele. A issue não diz em qual arquivo essa configuração está. Presume-se `config/initializers/datetime.rb` ou o próprio arquivo do patch. Se estiver no arquivo do patch, precisa ser preservada em outro lugar.
3. A aplicação roda em Rails 7.2, conforme a issue.
4. Sem o patch, `Date#to_s` volta ao comportamento nativo do Ruby: formato ISO `%Y-%m-%d` e nenhum argumento aceito. Chamadas `to_s(:formato)` passam a levantar `ArgumentError`.
5. O patch afeta apenas `Date`. `DateTime` e `Time` têm `to_s` próprio e não dependem dele. Isso precisa ser confirmado (ver Questões em Aberto).
6. A correção do fallback `to_default_s` já foi aplicada em separado, com specs. Esses specs testam o patch e, portanto, serão removidos ou substituídos junto com ele.
7. A skill `homologacao` (`.claude/skills/homologacao/`) está funcional e cobre as telas relevantes. A cobertura dela para PDFs, planilhas e notificações não é conhecida.
8. A localização via `l` usa um locale pt-BR já configurado no projeto. A existência e o conteúdo desse locale não estão confirmados na issue.

## Stack Tecnológica

- Ruby on Rails 7.2 (versão do Ruby não informada)
- active_scaffold (versão não informada)
- I18n do Rails para localização (`l`)
- Geração de PDF e de planilhas: bibliotecas não informadas na issue original
- Framework de testes: não informado na issue original. A issue menciona "specs", o que sugere RSpec, sem confirmação.

## Comandos

Não informado na issue original.

- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido
- Homologação: via a skill `homologacao` em `.claude/skills/homologacao/`. A forma exata de invocar é desconhecida.

## Estrutura do Projeto

Arquivos citados na issue:

```
config/initializers/fix_rails7_date_format.rb → patch a ser removido (criado em cbdb5bf7, 17/08/2023)
config/initializers/datetime.rb               → configura Time::DATE_FORMATS[:default] (sem patch)
lib/notifier.rb                               → exemplo de uso explícito de to_fs
.claude/skills/homologacao/                   → skill de comparação de telas antes/depois
```

Áreas a auditar, com caminhos desconhecidos:
- Views
- Geração de PDFs
- Geração de planilhas
- Templates de notificação
- Configurações e telas do active_scaffold
- Pontos que usam `to_param`, geração de URL e interpolação de `Date` em strings
- Localização dos specs que cobrem o patch (adicionados na correção separada): desconhecida

## Estilo de Código

Não há trecho real do código na issue, salvo a referência a `lib/notifier.rb`. As convenções abaixo vêm da própria proposta:

- Formatação para exibição deve ser **explícita**: `data.to_fs(:default)` ou `l(data)` (I18n).
- Não depender de `Date#to_s` nem de interpolação implícita (`"#{data}"`) para exibir datas ao usuário.
- Seguir o padrão já usado para `Time` em `lib/notifier.rb`.
- Critério para escolher entre `to_fs(:default)` e `l`: não informado (ver Questões em Aberto).

## Estratégia de Testes

- **Comparação visual e de conteúdo:** usar a skill `homologacao` para comparar telas antes e depois contra o mesmo banco. A skill **não normaliza datas**, então qualquer mudança de formato aparece como diferença. Esse é o principal mecanismo de validação.
- **Specs do patch:** os specs criados na correção do fallback `to_default_s` testam o comportamento do patch. Eles devem ser removidos ou trocados por specs que confirmem a ausência do patch, por exemplo `Date#to_s` devolvendo ISO e não aceitando argumento.
- **Usos indiretos:** os pontos de `to_param` e de geração de URL com datas devem ganhar cobertura que fixe o formato esperado, seja ISO ou outro aceito explicitamente.
- **PDFs, planilhas e notificações:** a cobertura da `homologacao` para esses artefatos é desconhecida. Se ela não os cobrir, será preciso validação complementar, por spec ou verificação manual.
- Framework, localização dos testes e meta de cobertura: não informado na issue original.

## Limites

- **Sempre:**
  - Formatar datas para exibição de forma explícita (`to_fs(:default)` ou `l`).
  - Rodar a `homologacao` antes e depois, contra o mesmo banco, e revisar toda diferença de data.
  - Auditar usos indiretos de `to_s`, como `to_param`, URLs e interpolação em strings.
  - Preservar a configuração de `Date::DATE_FORMATS[:default]`.
- **Perguntar antes:**
  - Aceitar qualquer mudança de formato visível ao usuário.
  - Mudar o formato de datas em URLs ou parâmetros, pois isso pode quebrar links salvos, integrações ou rotas.
  - Mudar arquivos de locale ou `DATE_FORMATS`.
  - Remover os specs criados na correção separada sem colocar substitutos.
  - Alterar configuração global do active_scaffold.
- **Nunca:**
  - Introduzir outro monkey-patch em `Date`, `DateTime` ou `Time` para compensar a remoção.
  - Configurar a `homologacao` para normalizar datas.
  - Remover o patch sem a auditoria dos pontos de uso.

## Critérios de Sucesso

1. `config/initializers/fix_rails7_date_format.rb` foi removido.
2. `Date::DATE_FORMATS[:default]` continua definido como `%d/%m/%Y`, e `Date.new(2023, 8, 17).to_fs(:default)` retorna `"17/08/2023"`.
3. `Date.new(2023, 8, 17).to_s` retorna `"2023-08-17"`, o comportamento nativo.
4. Não sobra no código nenhuma chamada `Date#to_s(<argumento>)`. Ela levantaria `ArgumentError`.
5. A `homologacao` contra o mesmo banco não mostra nenhuma diferença de formato de data em views e telas do active_scaffold. Toda diferença restante foi revisada e aprovada explicitamente.
6. PDFs, planilhas e templates de notificação exibem datas no mesmo formato de antes. Isso é verificado pela `homologacao` ou, se ela não cobrir esses artefatos, por outro meio documentado.
7. Os usos indiretos (`to_param`, geração de URL, interpolação em strings) foram listados. Para cada um, o formato resultante foi aceito ou ajustado, com registro da decisão.
8. Os specs do patch foram removidos ou substituídos, e a suíte de testes passa.

## Questões em Aberto

1. Em qual arquivo está configurado `Date::DATE_FORMATS[:default]`? Se for no próprio `fix_rails7_date_format.rb`, para onde a configuração deve ir (`config/initializers/datetime.rb`)?
2. Qual é o critério para escolher entre `to_fs(:default)` e `l`? Há preferência pelo I18n em views e por `to_fs` em código Ruby fora das views?
3. Existem rotas, links salvos, integrações externas ou parâmetros de busca que dependem de datas em `dd/mm/aaaa` na URL, via `to_param`? Se sim, o formato da URL deve mudar para ISO ou ser preservado explicitamente?
4. O código interpola `Date` em SQL bruto, em chaves de cache, em nomes de arquivo, em logs ou em payloads de integrações? Nesses casos, a mudança para ISO é desejada, pois pode corrigir comportamentos, ou deve ser mitigada?
5. A `homologacao` cobre PDFs, planilhas e templates de notificação, ou só telas HTML?
6. Como o active_scaffold renderiza colunas de data hoje: pelo `to_s` patchado ou pelo próprio formatador/I18n? Há configuração global dele que precise mudar?
7. Algum valor de campo de formulário (`value` de inputs de data) depende do `to_s` patchado e é reenviado e reinterpretado no servidor? A mudança para ISO afetaria o parse?
8. O patch também afeta `DateTime`, que herda de `Date`? Há uso de `DateTime` no projeto que precise da mesma auditoria?
9. Gems de terceiros usadas no projeto chamam `Date#to_s` esperando o formato brasileiro ou o formato ISO?
10. Os specs adicionados na correção do fallback `to_default_s` ficam em qual arquivo, e devem ser removidos ou reescritos como specs de regressão contra a volta do patch?
11. Quais são os comandos de teste e de execução da `homologacao` no projeto?