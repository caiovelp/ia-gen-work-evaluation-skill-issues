# Especificação: Correção de seis erros observados em produção (julho/2026)

## Objetivo

Corrigir seis defeitos independentes, identificados na análise dos e-mails `[SAPOS: Error]` de julho de 2026. A issue agrupa os seis apenas para vincular os commits. Cada defeito tem causa, correção e teste de regressão próprios.

**Usuários afetados:** alunos (itens 1, 2 e 5), candidatos em processo de admissão (itens 3 e 4) e usuários da simulação de notificação (item 6). O perfil exato do item 6 não foi informado.

**Por que corrigir:**
- Os itens 1 e 5 deixam o usuário sem saída na própria tela.
- Os itens 2, 4 e 6 transformam uma situação corriqueira em página de erro.
- O item 3 recusa um dado que o candidato vê preenchido na tela.
- O item 2 sozinho responde por quase metade do volume de e-mails de erro do mês.

### Itens

| # | Defeito | Comportamento esperado |
|---|---|---|
| 1 | O parcial `app/views/enrollments/_show_defense_committee_table.html.erb` usa o local `dismissal_date`, mas o chamador da tela do aluno não o passa. Ocorre `NameError` quando a matrícula está desligada, tem banca e não tem data de defesa. Foram atingidas duas matrículas, em duas instâncias. | O chamador da tela do aluno passa `dismissal_date`. O parcial lê o valor via `local_assigns`, de modo que um chamador que omita o local não quebre a página. |
| 2 | Um token de CSRF vencido gera `InvalidAuthenticityToken`, que o Rails converte em 422 com página estática. A página fala em "falta de permissão" e o erro dispara e-mail. O caso mais grave é o formulário longo de inscrição em disciplinas. | Um `rescue_from` no `ApplicationController` redireciona ao login com o motivo escrito. Requisição não-navegacional recebe 422, sem redirect. Sessão vazia não gera notificação. Sessão com conteúdo e token divergente continua notificando. |
| 3 | Os widgets compostos (cidade/estado/país, rua/número, local da formação escolar) só remontam o input escondido no evento `change`. Valores inseridos por autofill, gerenciador de senha ou script ficam de fora, e o servidor responde "não pode ficar em branco". | Nos três widgets, o input escondido é remontado também no evento `input` dos campos visíveis e no `submit` do formulário. |
| 4 | `Admissions::ApplyController` chama `params.require(:record)` sem tratamento. Um PUT que chega sem `record` (upload interrompido, duplo clique em "Modificar inscrição") gera `ParameterMissing` e a página crua de 400. | Um `before_action` em `create` e `update` devolve o candidato à inscrição com a mensagem "nenhuma alteração foi recebida". |
| 5 | `StudentEnrollmentController#_redirect_semester` levanta `CanCan::AccessDenied` quando não existe `ClassSchedule` para o ano/semestre pedido. O aluno recebe uma acusação de acesso indevido. | Semestre sem calendário vira redirect com mensagem informativa. Falta real de permissão continua levantando `AccessDenied`. A correção da #378 não havia coberto este ponto. |
| 6 | Na simulação de notificação, uma data impossível ainda levanta `Date::Error`, mesmo após a #530 ter passado a aceitar vários formatos no `strptime`. | O controller exibe um aviso e simula com a data padrão da notificação. |

### Issues relacionadas

- **#605:** mesmo sintoma do item 3 (o formulário passa no cliente e é recusado no servidor), mas o mecanismo é outro. No item 3 a validação do cliente passa corretamente, porque o campo visível está de fato preenchido.
- **#604:** trata do prejuízo de perder o preenchimento quando ocorre erro. Relaciona-se aos itens 2 e 3.
- **#378:** correção anterior que não alcançou o item 5.
- **#530:** antecessora do item 6.

## Premissas

1. O sistema é o SAPOS, uma aplicação Ruby on Rails que usa CanCan para autorização. Versões não informadas.
2. Os seis itens são independentes. Não se aplica decomposição em mapa de capacidades (Fase 0): o agrupamento existe só para rastrear commits, e cada item é especificado como uma correção isolada.
3. A issue está escrita no passado ("Suíte completa verde"), como relato de correções já feitas. Esta especificação a trata como definição do comportamento esperado, verificável pelos testes de regressão.
4. "Sessão vazia" (item 2) significa a sessão sem nenhum dado do usuário, típica de cookie expirado. O critério técnico exato não foi informado.
5. O envio de e-mail `[SAPOS: Error]` é feito por um mecanismo de notificação de exceções já existente. Qual mecanismo é não foi informado.
6. "Requisição não-navegacional" (item 2) abrange XHR/fetch e formatos diferentes de HTML. O critério de detecção não foi informado.
7. O "login" para onde o item 2 redireciona é a página de login já existente na aplicação.
8. A "data padrão da notificação" (item 6) é um valor que já existe no domínio da notificação.

## Stack Tecnológica

- Ruby on Rails, versão não informada.
- CanCan (`CanCan::AccessDenied`), versão não informada.
- JavaScript no cliente para os widgets compostos. Biblioteca e arquivos não informados.
- Demais dependências: não informado na issue original.

## Comandos

- Build: não informado na issue original.
- Testes: não informado na issue original.
- Lint: não informado na issue original.
- Dev: não informado na issue original.

## Estrutura do Projeto

Caminhos e símbolos citados na issue:

```
app/views/enrollments/_show_defense_committee_table.html.erb  → parcial da tabela da banca (item 1)
ApplicationController                                          → rescue_from de CSRF (item 2)
Admissions::ApplyController                                    → create/update da inscrição (item 4)
StudentEnrollmentController#_redirect_semester                 → seleção de semestre (item 5)
ClassSchedule                                                  → modelo de calendário do semestre (item 5)
```

Não informado na issue original:
- os arquivos dos chamadores do parcial (telas do aluno e do admin);
- os arquivos JavaScript dos três widgets compostos;
- o controller da simulação de notificação;
- a localização dos testes;
- os arquivos de tradução/mensagens.

## Estilo de Código

Não informado na issue original.

Convenção derivada da issue: em parciais, locais opcionais devem ser lidos via `local_assigns`, e não referenciados diretamente.

## Estratégia de Testes

- **Framework e localização dos testes:** não informado na issue original.
- **Teste de regressão por item:** cada item tem um teste que falha antes da correção e passa depois.
- **Testes de não-regressão:** onde a correção pode afetar quem já funcionava, há testes que passam antes e depois da correção.
  - Item 3: os três caminhos comuns de preenchimento, ou seja, digitação, autocomplete e submissão por Enter.
  - Item 5: o acesso à matrícula de outro aluno continua barrado com `AccessDenied`.
- **Item 3:** exige teste que execute JavaScript no navegador, para simular valor inserido sem evento `change`. A ferramenta usada não foi informada.
- **Item 2:** precisam ser cobertos quatro casos:
  1. sessão vazia: redirect e nenhuma notificação;
  2. sessão com conteúdo: redirect e notificação;
  3. requisição não-navegacional com sessão vazia: 422, sem redirect;
  4. requisição não-navegacional com sessão com conteúdo: 422, sem redirect, com notificação.
- **Cobertura mínima:** não informado na issue original.
- **Critério de aceite global:** suíte completa verde.

## Limites

**Sempre:**
- Escrever o teste de regressão de cada item antes da correção e confirmar que ele falha.
- Manter `CanCan::AccessDenied` para falta real de permissão (item 5).
- Manter a notificação por e-mail para token de CSRF divergente em sessão com conteúdo (item 2).
- Aplicar a correção do item 3 nos três widgets compostos, não só no de cidade/estado.
- Cobrir `create` e `update` na correção do item 4.

**Perguntar antes:**
- Desligar ou relaxar a proteção contra CSRF, ou alterar sua configuração global.
- Mudar o mecanismo de notificação de exceções.
- Alterar validações de servidor dos campos compostos.
- Alterar regras de autorização (habilidades do CanCan).
- Adicionar dependências.

**Nunca:**
- Desligar a notificação por e-mail de CSRF de forma incondicional.
- Transformar falta de permissão real em redirect informativo.
- Remover ou enfraquecer testes existentes para fazer a suíte passar.

## Critérios de Sucesso

**Item 1**
1. O aluno abre a página da própria matrícula quando ela está desligada, tem banca e não tem data de defesa, sem `NameError`.
2. O parcial renderiza sem erro mesmo quando um chamador não passa `dismissal_date`.
3. A tela do admin continua funcionando como antes.

**Item 2**
4. Um POST navegacional com token inválido e sessão vazia redireciona ao login com uma mensagem que explica a sessão expirada, e não envia e-mail.
5. Um POST navegacional com token inválido e sessão com conteúdo redireciona ao login e envia a notificação.
6. Uma requisição não-navegacional com token inválido recebe 422, sem redirect.
7. A mensagem exibida não menciona falta de permissão.

**Item 3**
8. Um valor inserido nos campos visíveis sem disparar `change` chega ao servidor no input escondido, nos três widgets.
9. A submissão por Enter envia o composto atualizado.
10. Os caminhos de digitação e autocomplete continuam funcionando.

**Item 4**
11. Um PUT ou POST em `Admissions::ApplyController` sem `record` não gera 400. O candidato volta à inscrição com a mensagem "nenhuma alteração foi recebida".

**Item 5**
12. Pedir um ano/semestre sem `ClassSchedule` resulta em redirect com mensagem informativa, sem `AccessDenied`.
13. O acesso à matrícula de outro aluno continua levantando `AccessDenied`.

**Item 6**
14. Uma data de consulta impossível na simulação de notificação gera um aviso visível, e a simulação usa a data padrão da notificação, sem `Date::Error`.
15. As datas válidas nos formatos já aceitos pela #530 continuam funcionando.

**Global**
16. Cada item tem um teste de regressão que falha antes da correção e passa depois.
17. A suíte completa passa.
18. Espera-se que o volume de e-mails `[SAPOS: Error]` causados por esses seis defeitos caia a zero. A forma de medir não foi informada.

## Questões em Aberto

1. **Item 1:** qual arquivo é o chamador da tela do aluno? Qual deve ser o comportamento do parcial quando `dismissal_date` não é passado: tratar como `nil` ou usar outro padrão?
2. **Item 2:** qual é o critério exato de "sessão vazia"? Que chaves da sessão contam como conteúdo?
3. **Item 2:** como classificar uma requisição como não-navegacional: `request.xhr?`, formato da requisição, cabeçalho `Accept` ou `Sec-Fetch-Mode`?
4. **Item 2:** se o usuário ainda estiver autenticado (sessão com conteúdo), o redirect deve ser mesmo para o login ou de volta à página de origem?
5. **Item 2:** qual é o texto exato da mensagem? Ele será internacionalizado?
6. **Item 2:** o prejuízo de perder o formulário longo de inscrição em disciplinas fica integralmente para a #604, ou esta issue deve preservar algo?
7. **Item 3:** quais são os arquivos e componentes dos três widgets? Remontar no `submit` deve acontecer antes de qualquer validação de cliente já existente?
8. **Item 4:** para qual página exatamente o candidato volta em `create` (formulário novo) e em `update` (edição da inscrição existente)? O redirect deve preservar algum estado?
9. **Item 5:** para onde deve ir o redirect (semestre corrente, lista de semestres?) e qual é o texto da mensagem informativa?
10. **Item 6:** qual controller e ação fazem a simulação de notificação? Qual é a "data padrão da notificação"? Qual é o texto do aviso?
11. **Geral:** quais são o framework de testes, os comandos de build/teste/lint e a ferramenta de testes com JavaScript usados no projeto?
12. **Geral:** a issue descreve as correções como já feitas. Esta especificação serve para validar retroativamente o que foi implementado, ou para orientar uma nova implementação?