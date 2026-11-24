# Spec: Correção do erro de JavaScript nas telas de simulação de notificações e asserções

## Objetivo

Eliminar o erro de JavaScript não tratado que ocorre no carregamento das telas de simulação:

- `/notifications/:id/simulate`
- `/assertions/:id/simulate`

Erro observado no console do navegador:

```
Uncaught TypeError: Cannot read properties of undefined (reading 'replace')
```

**Contexto:** a consulta roda normalmente no backend e a página renderiza. Porém o script do formulário de parâmetros interrompe a execução nesse ponto. Assim, todo comportamento que esse script registraria depois da linha com falha deixa de existir.

**Origem identificada na issue:** o mesmo trecho aparece em três parciais.

| Parcial | Linha |
|---|---|
| `app/views/notifications/_params_form.html.erb` | 79 |
| `app/views/queries/_params_form.html.erb` | 70 |
| `app/views/assertions/_params_form.html.erb` | 62 |

```javascript
var p = link.prop("search").replace(/^\?/, "");
```

`link.prop("search")` retorna `undefined` em dois casos: quando o elemento referenciado não é uma âncora, ou quando o objeto jQuery está vazio. A chamada `.replace` seguinte então falha.

**A correção tem dois objetivos:**

1. **Robustez:** tratar a ausência de `search` sem lançar exceção, por exemplo tratando o valor ausente como string vazia.
2. **Causa raiz:** verificar se o seletor que origina `link` encontra o elemento esperado nas três parciais. Se o seletor estiver errado, a proteção sozinha só esconderia uma funcionalidade quebrada.

**Usuário afetado:** quem usa as telas de simulação de notificações e asserções. O ambiente onde o problema foi visto é a homologação.

**Fora de escopo:** não se trata de regressão de upgrade. O erro ocorre igualmente no Rails 7.1 e no 7.2.

## Premissas

1. O objeto `link` é um objeto jQuery. A issue usa `.prop(...)`, o que indica isso.
2. O valor de `p` é a query string sem o `?` inicial e serve para montar ou preencher parâmetros do formulário. A finalidade exata não está descrita na issue.
3. A parcial `queries/_params_form.html.erb` tem o mesmo defeito latente e deve receber a mesma correção. Isso vale mesmo que a issue não cite uma tela de simulação de queries com erro.
4. Uma string vazia como valor de `p` é um estado válido, que significa "sem parâmetros", e o código seguinte lida com ele sem efeitos colaterais.
5. A correção se limita ao JavaScript das parciais e ao seletor. Não há mudança no backend, nas rotas nem nos controllers.

## Stack Tecnológica

- Ruby on Rails, versões 7.1 e 7.2, conforme a issue.
- Views ERB com JavaScript embutido nas parciais.
- jQuery, inferido pelo uso de `.prop`. A versão não foi informada na issue original.

## Comandos

Não informado na issue original.

- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Só os caminhos citados na issue são conhecidos:

```
app/views/notifications/_params_form.html.erb → formulário de parâmetros de notificações
app/views/queries/_params_form.html.erb       → formulário de parâmetros de queries
app/views/assertions/_params_form.html.erb    → formulário de parâmetros de asserções
```

O local dos testes (unitários, de sistema ou de JS) não foi informado na issue original.

## Estilo de Código

Não informado na issue original. O único trecho disponível é a linha com falha, citada acima. A convenção a seguir deve ser a já usada nas próprias parciais: jQuery e `var`.

## Estratégia de Testes

O framework de testes não foi informado na issue original. A verificação mínima esperada é:

- **Manual:** abrir `/notifications/:id/simulate` e `/assertions/:id/simulate` e confirmar que o console do navegador não mostra erro no carregamento.
- **Manual:** confirmar que a funcionalidade dependente de `link` continua operando quando o elemento existe e tem query string.
- **Automatizado (se existir infraestrutura de testes de sistema com JS):** um teste que carregue cada tela de simulação e falhe se houver erro de JavaScript no console. Deve incluir o cenário em que `link` não resolve para uma âncora.
- **Regressão:** verificar também a tela que usa `queries/_params_form.html.erb`.

## Limites

- **Sempre:**
  - Aplicar a correção de forma consistente nas três parciais.
  - Verificar o seletor de `link`, além de proteger o `.replace`.
  - Validar no console do navegador as telas afetadas.
- **Perguntar antes:**
  - Extrair o JavaScript duplicado para um arquivo ou módulo compartilhado.
  - Alterar a marcação HTML de forma que afete outras telas.
  - Adicionar dependências.
  - Alterar o comportamento funcional do formulário de parâmetros além do necessário.
- **Nunca:**
  - Silenciar o erro com `try/catch` genérico, escondendo um seletor quebrado.
  - Alterar o backend ou as rotas para resolver um problema de frontend.
  - Remover a funcionalidade que depende de `link`.

## Critérios de Sucesso

1. Carregar `/notifications/:id/simulate` não gera nenhum `Uncaught TypeError` nem outro erro de JavaScript no console.
2. Carregar `/assertions/:id/simulate` não gera nenhum `Uncaught TypeError` nem outro erro de JavaScript no console.
3. Nas três parciais, a ausência de `search` em `link`, seja por objeto jQuery vazio ou por elemento que não é âncora, é tratada como string vazia, sem exceção.
4. O seletor que define `link` foi revisado nas três parciais. Ele encontra o elemento esperado, ou a issue registra por que a ausência do elemento é legítima.
5. O script do formulário de parâmetros executa até o fim nas telas de simulação, e o comportamento que vem depois da linha corrigida volta a funcionar.
6. O comportamento das telas que usam `queries/_params_form.html.erb` continua igual ou melhora, sem regressão.
7. O resultado é o mesmo em Rails 7.1 e 7.2.

## Perguntas em Aberto

1. Qual elemento `link` deveria referenciar e qual é o seletor usado? Nas telas de simulação ele deveria existir, ou sua ausência é esperada?
2. Qual é a finalidade de `p` (a query string sem `?`)? Quais funcionalidades da tela deixam de funcionar hoje porque o script é interrompido?
3. Existe uma tela de simulação de queries (algo como `/queries/:id/simulate`) que use `queries/_params_form.html.erb` e apresente o mesmo erro? Ou a parcial de queries só é usada em contextos onde `link` sempre existe?
4. A correção deve ficar restrita às três parciais, ou é desejável consolidar o JavaScript duplicado num único lugar?
5. Há infraestrutura de testes de sistema com JavaScript (por exemplo, testes de navegador) para cobrir a regressão? Quais são os comandos de teste e lint do projeto?
6. Qual versão de jQuery é usada? Há outros pontos no código com o mesmo padrão `.prop("search").replace(...)` além das três parciais citadas?