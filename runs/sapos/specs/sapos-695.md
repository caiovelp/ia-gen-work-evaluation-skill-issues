# Spec: Impedir que o `node_modules` versionado divirja do `yarn.lock`

## Objetivo

Garantir que a cópia versionada de `node_modules/codemirror` corresponda sempre ao que `package.json` e `yarn.lock` declaram. A guarda deve rodar no PR, onde o erro acontece.

**Por que isso importa.** O `node_modules/codemirror` é versionado de propósito, com 337 arquivos. Esse arranjo foi reavaliado e mantido na #682, pelos seguintes motivos:

- O `config/initializers/assets.rb:11` coloca `node_modules` no asset load path do Sprockets.
- O `app/assets/javascripts/application.js:17-23` carrega `codemirror/lib/codemirror`, os modes `javascript`, `sql`, `xml` e `htmlmixed`, e o addon `mode/overlay`.
- O `application.css.scss:18` importa o CSS do CodeMirror.
- Nenhum dos guias de instalação da wiki (`Quick-install`, `Explained-Quick-install-for-development`, `Explained-quick-install-for-production`) exige node, yarn ou npm. O procedimento vai de `git clone` direto a `rake assets:precompile`.
- O CI também não instala node.

**O defeito atual.** A pasta divergiu dos manifestos:

| arquivo (todos versionados) | versão |
|---|---|
| `package.json` | `^5.58.2` |
| `yarn.lock` | 5.58.2 |
| `node_modules/codemirror/package.json` | **5.55.0** |
| `node_modules/.yarn-integrity` | `codemirror@^5.55.0` |

Na prática, o CodeMirror que compila é o 5.55.0, e não o 5.58.2 anunciado pelo lock. Hoje nada no repositório detecta essa divergência.

Há um problema relacionado no `.gitignore`. Ele contém `/node_modules/` desde c51b064a (16/05/2024), mas a pasta já estava rastreada desde c72f6080 (01/07/2020, #331). A linha não tem efeito nenhum e leva quem lê o arquivo a concluir o contrário do que o repositório faz.

**Usuários:**

- Mantenedores que atualizam dependências JS.
- Revisores de PR.
- Quem instala a aplicação seguindo a wiki, sem node.

**Histórias / critérios de aceitação:**

1. Como revisor, quero que o CI falhe quando um PR altera `package.json` ou `yarn.lock` sem atualizar a pasta versionada correspondente, ou o contrário.
2. Como mantenedor, quero rodar localmente `rake javascript:check` e obter uma mensagem que diga qual arquivo diverge de qual, e com quais valores.
3. Como instalador, quero que o CodeMirror compilado seja o declarado no lock (5.58.2).
4. Como leitor do repositório, quero que o `.gitignore`, a skill `dependencias` e a wiki digam a verdade: o `node_modules` é versionado de propósito, e a documentação explica como atualizá-lo.

**Escopo (da issue):**

- [ ] `rake javascript:check`, comparando `package.json`, `yarn.lock`, `node_modules/<pacote>/package.json` e `node_modules/.yarn-integrity`, e falhando nas duas direções.
- [ ] Passo no job `checks` do CI.
- [ ] Sincronizar a pasta versionada com o lock (5.55.0 → 5.58.2).
- [ ] Remover `/node_modules/` do `.gitignore`.
- [ ] Registrar na skill `dependencias` e na wiki que o `node_modules` é versionado de propósito e como se atualiza.

**Fora de escopo (limite conhecido, aceito na issue):**

- Detectar edição manual de arquivos dentro de `node_modules/codemirror`.
- Detectar `yarn install` interrompido pela metade.
- Manter um manifesto de hashes por arquivo.
- Aritmética de semver.
- Desversionar `node_modules`.

## Premissas

1. O projeto é uma aplicação Rails com Sprockets, já que menciona `config/initializers`, `app/assets` e `rake assets:precompile`.
2. O yarn em uso é o Yarn 1 (classic), porque existem `.yarn-integrity` e `yarn.lock`. O formato do lock é o v1: entradas cujas chaves são uma ou mais especificações `pacote@faixa` separadas por vírgula, cada uma com um campo `version`.
3. A invariante a verificar é a descrita na issue, sem semver:
   - (a) a faixa declarada em `package.json` aparece entre as especificações da chave de uma entrada do `yarn.lock`;
   - (b) a `version` dessa entrada é igual à `version` de `node_modules/<pacote>/package.json`;
   - (c) o `.yarn-integrity` registra o mesmo padrão `pacote@faixa` declarado em `package.json`.
4. O campo `systemParams` do `.yarn-integrity` é ignorado, porque varia conforme a máquina.
5. A versão instalada é lida exclusivamente de `node_modules/<pacote>/package.json`.
6. A checagem roda sem node, sem rede e sem banco: só leitura de JSON e uma regex no `yarn.lock`. Por isso a task rake não deve depender de `:environment`, se isso significar carregar banco.
7. A checagem itera sobre os pacotes declarados em `package.json`. Hoje esse é só `codemirror`, mas a checagem não fixa o nome em código.
8. O CodeMirror 5 não traz dependências transitivas a versionar. Se trouxer, isso vira questão em aberto (ver Q3).
9. O formato a seguir é o de `rake seeds:check` com o job `seed`, e o de `spec/config/schema_dump_spec.rb` com o passo "Schema dump" do job `checks`.
10. A sincronização 5.55.0 → 5.58.2 é feita uma única vez, por um mantenedor com yarn instalado localmente. O resultado é o tarball publicado descompactado, sem nenhum artefato gerado por nós.
11. Os caminhos usados por `application.js:17-23` e `application.css.scss:18` continuam existindo no CodeMirror 5.58.2. Isso precisa ser confirmado na sincronização.

## Stack Tecnológica

- Ruby / Rails, com o Sprockets como pipeline de assets. As versões não foram informadas na issue.
- Rake, para `rake seeds:check`, `rake assets:precompile` e o novo `rake javascript:check`.
- Yarn 1 (premissa 2) e `package.json`, usados apenas por mantenedores, fora do CI e da instalação.
- CodeMirror: `^5.58.2` declarado, 5.55.0 instalado hoje.
- CI com os jobs `checks` e `seed`. A plataforma de CI não foi informada na issue.
- Framework de testes: possivelmente RSpec, a julgar por `spec/config/schema_dump_spec.rb`. A versão não foi informada na issue.

## Comandos

- Checagem nova (a criar): `rake javascript:check`
- Checagens existentes de referência: `rake seeds:check`
- Pré-compilação de assets: `rake assets:precompile`
- Atualização da pasta versionada (só para mantenedores): `yarn install`. As flags exatas não foram informadas na issue.
- Comandos de testes, lint, build e dev: não informados na issue original.

## Estrutura do Projeto

Arquivos e caminhos citados na issue:

```
package.json                                  → declaração das dependências JS (versionado)
yarn.lock                                     → lock do Yarn (versionado)
node_modules/codemirror/                      → tarball do CodeMirror descompactado, 337 arquivos (versionado de propósito)
node_modules/.yarn-integrity                  → metadados do yarn (versionado; systemParams é ignorado)
.gitignore                                    → contém hoje a linha /node_modules/, que deve sair
config/initializers/assets.rb                 → linha 11: node_modules no asset load path
app/assets/javascripts/application.js         → linhas 17-23: requires do CodeMirror
application.css.scss                          → linha 18: import do CSS do CodeMirror (caminho completo não informado)
spec/config/schema_dump_spec.rb               → referência de checagem do mesmo tipo
```

Caminhos não informados na issue:

- Onde definir a task `javascript:check`, e onde está definida a `seeds:check`.
- A definição dos jobs de CI.
- A skill `dependencias`.
- Onde ficariam os testes da nova task.

## Estilo de Código

Não informado na issue original. Seguir o estilo de `rake seeds:check` e de `spec/config/schema_dump_spec.rb`, que não estão visíveis aqui.

## Estratégia de Testes

- **Testes unitários da lógica de comparação**, com fixtures mínimos dos quatro arquivos, sem tocar o `node_modules` real. Casos a cobrir:
  - Tudo consistente: passa.
  - Lock à frente da pasta (lock 5.58.2, instalado 5.55.0): falha. É o caso atual.
  - Pasta à frente do lock (instalado mais novo que o `version` do lock): falha.
  - Faixa do `package.json` ausente das chaves do `yarn.lock`, por exemplo `package.json` alterado sem rodar `yarn`: falha.
  - Chave do `yarn.lock` com várias especificações separadas por vírgula, uma delas casando: passa.
  - Padrão `pacote@faixa` no `.yarn-integrity` diferente do `package.json` (o `^5.55.0` atual contra `^5.58.2`): falha.
  - `systemParams` diferente entre fixtures: não afeta o resultado.
  - Arquivo ausente (`node_modules/<pacote>/package.json` ou `.yarn-integrity`): falha com mensagem clara.
- **Teste de integração no CI:** `rake javascript:check` contra o repositório real, como passo do job `checks`. O passo deve falhar no estado atual e passar depois da sincronização.
- **Verificação da sincronização:** `rake assets:precompile` conclui sem erro e o editor CodeMirror funciona na aplicação, com os modes `javascript`, `sql`, `xml`, `htmlmixed` e o addon `mode/overlay`.
- O framework, o local dos testes e a cobertura esperada não foram informados na issue (ver Q6).

## Limites

- **Sempre:**
  - Rodar a checagem sem node, sem rede e sem banco.
  - Ignorar `systemParams`.
  - Ler a versão instalada de `node_modules/<pacote>/package.json`.
  - Falhar nas duas direções, com mensagem que indique o arquivo, o pacote e os valores divergentes.
  - Manter `node_modules` versionado.
- **Perguntar antes:**
  - Adicionar gems ou dependências novas.
  - Alterar a estrutura dos jobs de CI além de acrescentar o passo em `checks`.
  - Mudar a faixa declarada no `package.json`, ou atualizar além de 5.58.2.
  - Estender a checagem a dependências transitivas ou a pastas extras em `node_modules`.
  - Escolher qual página da wiki recebe a documentação.
- **Nunca:**
  - Desversionar `node_modules`.
  - Editar à mão arquivos dentro de `node_modules/codemirror`.
  - Introduzir artefatos gerados (minificados, `dist/`).
  - Exigir node ou yarn na instalação ou no CI.
  - Comparar `systemParams`.
  - Implementar aritmética de semver.

## Critérios de Sucesso

1. `rake javascript:check` existe e retorna falha (código de saída não zero) no estado atual do repositório. A mensagem cita `codemirror`, 5.58.2 (lock) contra 5.55.0 (instalado) e `^5.55.0` no `.yarn-integrity`.
2. A checagem falha quando o lock está à frente da pasta e também quando a pasta está à frente do lock.
3. A checagem não exige node, rede nem banco.
4. A checagem ignora `systemParams` do `.yarn-integrity`.
5. O job `checks` do CI tem um passo que executa `rake javascript:check`, e um PR com divergência fica vermelho.
6. Depois da sincronização:
   - `node_modules/codemirror/package.json` indica 5.58.2;
   - `node_modules/.yarn-integrity` registra `codemirror@^5.58.2`;
   - `rake javascript:check` passa;
   - `rake assets:precompile` passa;
   - os requires de `application.js:17-23` e o import de `application.css.scss:18` resolvem.
7. A pasta sincronizada contém apenas o tarball publicado descompactado, sem `dist/` nem minificados gerados por nós.
8. `/node_modules/` não consta mais do `.gitignore`.
9. A skill `dependencias` e a wiki explicam que o `node_modules` é versionado de propósito, por quê (Sprockets, instalação e CI sem node, #682) e o procedimento de atualização: alterar `package.json`, rodar `yarn install`, commitar `yarn.lock`, `node_modules/` e `.yarn-integrity`, e rodar `rake javascript:check`.

## Questões em Aberto

1. **Escopo de pacotes.** A checagem deve iterar sobre `dependencies` e `devDependencies`, ou só `dependencies`? Hoje há apenas `codemirror`, mas a issue usa `<pacote>`.
2. **Comparação com o `.yarn-integrity`.** Além de `topLevelPatterns`, a checagem deve olhar outros campos, como `lockfileEntries`? Ou basta conferir o padrão `pacote@faixa`?
3. **Conteúdo extra em `node_modules`.** Pastas de pacotes que não constam em `package.json` ou `yarn.lock`, ou dependências transitivas, devem fazer a checagem falhar?
4. **Carga do ambiente Rails.** Onde fica a task e de que ela depende? Ela deve evitar carregar o ambiente Rails, para não exigir banco no job `checks`?
5. **Testes.** Os testes da lógica devem seguir o modelo de `spec/config/schema_dump_spec.rb`, como um spec que roda contra o repositório real, ou também ter testes unitários com fixtures?
6. **Comandos de teste.** Qual é o comando exato para rodar os testes localmente e no CI?
7. **Versão do yarn.** Que versão do yarn deve ser usada na sincronização, e com quais flags, para reproduzir o formato atual do `yarn.lock` e do `.yarn-integrity`?
8. **Documentação.** Em qual página da wiki entra a documentação: uma nova ou um dos três guias de instalação? E onde fica a skill `dependencias`?
9. **Compatibilidade da versão nova.** Houve alguma mudança entre 5.55.0 e 5.58.2 que afete os modes e o addon usados? É preciso validação manual específica no editor?
10. **Hooks locais.** A checagem deve entrar também numa task agregadora local, como uma eventual task padrão de checks, se existir?