# Especificação: Cobertura das notificações por e-mail no fluxo de inscrição em disciplinas

## Premissas

1. O projeto é uma aplicação Ruby on Rails testada com RSpec. A issue cita `spec/requests/...`, `ActionMailer::Base.deliveries`, active_scaffold e `ability.rb`.
2. A autorização usa CanCan/CanCanCan, porque `ability.rb` usa `alias_action`. A versão é desconhecida.
3. Em ambiente de teste, o ActionMailer usa o método de entrega `:test`. Por isso `ActionMailer::Base.deliveries` acumula as mensagens enviadas.
4. A entrega é síncrona no teste, ou a fila é processada dentro do spec. Se o envio for assíncrono (`deliver_later`), as asserções precisam de ajuste.
5. Os "sete passos" do processo vêm de um documento ou especificação do processo que não está na issue. A numeração (2 = aluno pede, 3 = orientador decide, 5 = secretaria efetiva, 4/6/7 = remoção e ajustes) segue o texto da issue.
6. O congelamento de relógio usa um mecanismo já disponível na suíte, como `travel_to` ou Timecop. Qual deles a suíte usa é desconhecido.
7. Este ramo cobre só os passos 2, 3 e 5. Os passos 4, 6 e 7 e o problema de homologação ficam fora do escopo desta entrega.
8. O spec fixa o comportamento atual (*characterization test*). Ele não altera código de produção.

## Objetivo

O período de inscrição em disciplinas tem data marcada, e três dos sete passos do processo dependem de e-mail por design:

- No passo 2, o e-mail ao aluno funciona como "uma forma de recibo".
- No passo 3, "o aluno será notificado da decisão".
- No passo 5, a secretaria efetiva a inscrição e o aluno recebe aviso.

Se a notificação falha, o aluno não sabe que o pedido foi registrado e o orientador não sabe que tem pedido para avaliar. O passo 4 nunca começa.

Situação atual: o `EmailTemplate` define onze templates ligados ao fluxo, oito deles chamados pelos controllers. Nenhum é exercitado por spec algum, e nenhum teste confere `ActionMailer::Base.deliveries` neste fluxo. Existem 2477 linhas de spec sobre inscrição, todas sobre tela, estado e validação.

**O que construir:** um request spec (rápido, sem navegador) que fixe a quantidade e os destinatários dos e-mails enviados em cada ponto coberto do fluxo. Ele deve detectar regressões silenciosas, em especial um orientador deixar de ser avisado.

**Usuários afetados pelo comportamento testado:** aluno, orientador(es) e secretaria.
**Usuário do artefato:** a equipe de desenvolvimento, que ganha uma rede de proteção contra regressão.

**Comportamentos a fixar:**

| Passo | Ação | Comportamento esperado |
|---|---|---|
| 2 | Aluno submete o pedido | 3 destinatários: o aluno e cada um dos orientadores, no caso de dois orientadores |
| 3 | Orientador salva o pedido (radios por disciplina + comentário geral) | 1 e-mail, contendo o comentário geral e as listas de disciplinas alteradas e mantidas |
| 3 | Orientador decide várias disciplinas de uma vez | Ainda 1 e-mail, não um por disciplina |
| 3 | Orientador salva sem nenhuma mudança | 0 e-mails |
| 3 | Ícones "Válido"/"Inválido" na lista de `class_enrollment_requests` | 0 e-mails (comportamento atual, ver Perguntas em Aberto) |
| 5 | Secretaria efetiva | 1 e-mail ao aluno |

## Stack Tecnológica

- Ruby on Rails (inferido). Versão não informada na issue original.
- RSpec, com request specs. Versão não informada na issue original.
- ActionMailer.
- active_scaffold, que é responsável pelo formulário aninhado de `class_enrollment_requests`.
- CanCan/CanCanCan (`ability.rb`, inferido).
- Modelo `EmailTemplate` para os textos das notificações.
- Biblioteca de congelamento de tempo: não informada na issue original.

## Comandos

Não informado na issue original.

- Executar o spec: desconhecido. A forma usual em projetos RSpec seria algo como `bundle exec rspec spec/requests/enrollment_request_flow_spec.rb`, mas não foi confirmado.
- Suíte completa, lint e build: desconhecidos.

## Estrutura do Projeto

Só o que aparece na issue:

```
spec/requests/enrollment_request_flow_spec.rb  → spec novo deste ramo
ability.rb                                      → regras de autorização (caminho exato desconhecido)
EmailTemplate                                   → modelo com os templates de e-mail (caminho desconhecido)
ClassSchedule#enroll_open?                      → janela de inscrição, depende de Time.now
```

Rotas citadas:

- `/enrollment/:id`
- `/enrollment/:id/enroll/:ano-:semestre`

Controllers, mailers e localização das factories e fixtures: não informado na issue original.

## Estilo de Código

Não informado na issue original. Convenções inferíveis da issue:

- Usar request specs, não specs de sistema com navegador.
- Fazer as asserções sobre `ActionMailer::Base.deliveries`, contando as mensagens e conferindo os destinatários.
- Registrar no próprio spec, como comentário, as armadilhas que fariam o teste passar ou falhar pelo motivo errado. Elas estão listadas abaixo.

## Estratégia de Testes

- **Nível:** request spec, sem navegador.
- **Framework:** RSpec.
- **Local:** `spec/requests/enrollment_request_flow_spec.rb`.
- **Asserções:** quantidade de e-mails em `ActionMailer::Base.deliveries`, destinatários e, no passo 3, presença do comentário geral e das listas de alteradas e mantidas.
- **Isolamento:** limpar `deliveries` entre os cenários, ou medir a diferença antes e depois de cada ação.
- **Cenário crítico:** pedido com dois orientadores. O envio percorre `enrollment.advisements`, e um laço que não executa deixaria um orientador sem aviso sem gerar erro algum.

**Armadilhas que o spec deve tratar e documentar:**

1. **Parâmetros do formulário do orientador.** O formulário submete quatro campos por pedido (`id`, `course_class`, `class_enrollment`, `status`) mais uma entrada `"0"` vazia. O spec precisa reproduzir isso fielmente:
   - Com o nome errado (`..._attributes`), o status não muda e o e-mail sai só por causa do comentário. O teste fica verde sem exercitar a decisão.
   - Enviando só o `status`, o active_scaffold destrói os pedidos que considera ausentes.
2. **Situação de matrícula.** Ela precisa ter `user: true`. Sem isso, `_valid_enrollment` levanta `AccessDenied` e o aluno não chega à tela.
3. **Relógio.** `ClassSchedule#enroll_open?` usa `Time.now`. O spec deve congelar o tempo dentro da janela de inscrição para não depender da data de execução.
4. **Orientador principal.** A validação "um dos orientadores deve ser principal" olha a coleção, e o objeto em memória não enxerga registros recém-criados. É necessário `reload` antes de validar.

**Cobertura esperada:** os seis cenários da tabela do Objetivo. Não há meta percentual informada.

## Limites

- **Sempre:**
  - Garantir que cada asserção de "0 e-mails" seja precedida por uma ação que de fato altera ou tenta alterar o estado. Caso contrário, o zero não prova nada.
  - Confirmar a mudança de status no banco junto com a contagem de e-mails, para não repetir a armadilha 1.
  - Congelar o relógio em todos os cenários que dependem da janela de inscrição.
  - Manter o spec rápido, sem navegador.
- **Perguntar antes:**
  - Alterar código de produção, por exemplo fazer os ícones "Válido"/"Inválido" notificarem.
  - Alterar `ability.rb` ou o `set_status`.
  - Adicionar gems, como uma biblioteca de tempo, se ainda não existir.
  - Ampliar o escopo para os passos 4, 6 e 7 ou para a ferramenta de homologação.
- **Nunca:**
  - Escrever asserções que passam sem exercitar a decisão do orientador.
  - Depender da data real de execução.
  - Remover ou afrouxar specs existentes do fluxo de inscrição.
  - Enviar e-mails reais.

## Critérios de Sucesso

- [ ] **Passo 2:** um aluno com dois orientadores submete o pedido e o spec verifica exatamente 3 destinatários: o aluno e cada orientador individualmente.
- [ ] **Passo 3, salvar com decisão:** o spec verifica exatamente 1 e-mail ao aluno, contendo o comentário geral e as listas de alteradas e mantidas, e o status dos pedidos muda no banco.
- [ ] **Passo 3, várias disciplinas decididas de uma vez:** o spec verifica exatamente 1 e-mail.
- [ ] **Passo 3, salvar sem mudança:** o spec verifica 0 e-mails, e os pedidos não são destruídos.
- [ ] **Passo 3, ícones "Válido"/"Inválido":** o spec verifica 0 e-mails e que o status mudou. Fica fixado o comportamento atual.
- [ ] **Passo 5:** a secretaria efetiva e o spec verifica exatamente 1 e-mail ao aluno.
- [ ] As quatro armadilhas estão tratadas no código do spec e explicadas em comentários.
- [ ] O spec passa de forma determinística independentemente da data de execução.
- [ ] Se o laço sobre `enrollment.advisements` for quebrado (zero iterações), o spec do passo 2 falha.

## Perguntas em Aberto

1. **Ícones "Válido"/"Inválido" sem notificação:**
   - É deliberado ou é defeito? Hoje `set_status` só notifica quando recebe bloco, e só `set_effected` passa um. O `alias_action :set_invalid, :set_requested, :set_valid, to: :update` expõe esses ícones ao orientador.
   - Se for defeito, o cenário deve ser marcado como pendente ou falho conhecido até o conserto, em vez de fixar "0"?
2. **Templates sem cobertura:** quais dos onze templates do `EmailTemplate` correspondem a quais passos? Os três templates não chamados por nenhum controller são código morto, são usados por outro caminho (jobs, models) ou são lacuna de implementação?
3. **Passos 4, 6 e 7:** a remoção pelo aluno e o período de ajustes, com ação `REMOVE` além de `INSERT`, entram nesta issue ou em uma issue ou ramo separado?
4. **Homologação:** a captura loga com um único usuário e não alcança as rotas do aluno (`/enrollment/:id`, `/enrollment/:id/enroll/:ano-:semestre`), que exigem `ROLE_ALUNO` com `student` associado. Isso deve ser resolvido aqui? O que é essa ferramenta de captura das 125 rotas e onde ela fica?
5. **Passo 3, conteúdo:** além do comentário geral, o spec deve conferir o conteúdo das listas de alteradas e mantidas, ou só a contagem e o destinatário?
6. **Passo 3, destinatários:** o e-mail da decisão vai só ao aluno, ou também com cópia aos demais orientadores?
7. **Passo 5:** o e-mail de efetivação também deveria ir aos orientadores?
8. **Envio:** a entrega é síncrona (`deliver_now`) ou assíncrona (`deliver_later`) nesse fluxo?
9. **Execução:** quais são os comandos oficiais para rodar o spec e a suíte, e qual biblioteca de congelamento de tempo o projeto já usa?