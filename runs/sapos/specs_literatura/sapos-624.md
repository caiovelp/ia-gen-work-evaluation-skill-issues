# Erro de JavaScript nas telas de simulação de notificações e asserções

## Resumo

As telas de simulação de notificações (`/notifications/:id/simulate`) e de asserções (`/assertions/:id/simulate`) disparam um erro de JavaScript não tratado ao carregar: `TypeError: Cannot read properties of undefined (reading 'replace')`. O backend executa a consulta normalmente e a página é renderizada, mas o script do formulário de parâmetros para de executar.

Segundo a issue, `link.prop("search")` devolve `undefined` em dois casos:
- quando o elemento referenciado não é uma âncora;
- quando o objeto jQuery está vazio.

Nesses casos, a chamada seguinte a `.replace` falha. O mesmo trecho aparece em três parciais `_params_form.html.erb`, nas views de notificações, consultas e asserções.

## Passos para reproduzir

1. Abrir a tela de simulação de uma notificação qualquer (`/notifications/:id/simulate`) ou de uma asserção qualquer (`/assertions/:id/simulate`).
2. Abrir o console do navegador.
3. Observar o erro registrado durante o carregamento da página.

## Comportamento observado

- A consulta é executada normalmente no backend.
- A página é renderizada.
- O console mostra um `TypeError` não tratado.
- O script do formulário de parâmetros interrompe a execução.

## Comportamento esperado

A tela de simulação carrega sem erros de JavaScript e o script do formulário de parâmetros executa por completo.

## Stack trace / saída de erro

```
Uncaught TypeError: Cannot read properties of undefined (reading 'replace')
```

A issue original não traz o stack trace completo.

## Caso de teste

Não informado na issue original.

## Exemplo de código

O mesmo trecho aparece nos seguintes arquivos:

- `app/views/notifications/_params_form.html.erb:79`
- `app/views/queries/_params_form.html.erb:70`
- `app/views/assertions/_params_form.html.erb:62`

```javascript
var p = link.prop("search").replace(/^\?/, "");
```

## Versão e ambiente

- Encontrado durante uma varredura de rotas no ambiente de homologação.
- O erro ocorre de forma idêntica no Rails 7.1 e no Rails 7.2, portanto não é uma regressão do upgrade.
- Navegador e versão: não informados na issue original.