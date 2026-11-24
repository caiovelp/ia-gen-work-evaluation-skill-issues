# Seis erros observados em produção em julho/2026

## Resumo

A análise dos e-mails `[SAPOS: Error]` de julho de 2026 encontrou seis defeitos distintos. Cada um tem causa própria. Esta issue os agrupa para vincular os commits.

- **Itens 1 e 5:** o usuário fica sem saída na própria tela.
- **Itens 2, 4 e 6:** situações corriqueiras viram página de erro.
- **Item 3:** o servidor recusa um dado que o candidato vê preenchido na tela.

| # | Defeito |
|---|---------|
| 1 | A tela da matrícula, vista pelo aluno, quebra quando a matrícula está desligada, tem banca e não tem data de defesa. |
| 2 | Um token de CSRF vencido gera página de erro com mensagem inadequada e muitos e-mails. É quase metade do volume do mês. |
| 3 | O campo composto (cidade/estado/país, rua/número, local da formação escolar) não acompanha o que aparece na tela. |
| 4 | Uma submissão sem o parâmetro `record` derruba a inscrição do candidato. |
| 5 | Um semestre sem calendário cadastrado é tratado como tentativa de acesso indevido do aluno. |
| 6 | Uma data de consulta ilegível derruba a simulação de notificação. |

Issues relacionadas citadas no original:
- **#605:** mesmo sintoma do item 3, mecanismo diferente.
- **#604:** perda do preenchimento quando há erro.
- **#378:** a correção dela não cobriu o ponto do item 5.
- **#530:** o item 6 a complementa.

## Passos para reproduzir

**Item 1: tela do aluno com matrícula desligada**
1. Use uma matrícula desligada, com banca de defesa e com data de defesa nula.
2. Entre como o próprio aluno e abra a página da matrícula.
3. Para comparar, abra a mesma matrícula pela tela do admin. Ela abre normalmente.

**Item 2: token de CSRF vencido**
1. Abra a página de login, ou o formulário longo de inscrição em disciplinas.
2. Deixe a página aberta por horas, até o cookie de sessão expirar.
3. Envie o formulário.

**Item 3: campo composto não atualizado**
1. Abra um formulário com widget composto, por exemplo cidade/estado/país.
2. Preencha os campos visíveis de um jeito que não dispare o evento `change`. Exemplos: autofill do navegador, gerenciador de senha ou script.
3. Envie o formulário.

**Item 4: submissão sem `record`**
1. Na inscrição do candidato, provoque um PUT que contenha apenas `_method`, `authenticity_token` e `commit`. Isso acontece, por exemplo, com upload interrompido ou com duplo clique em "Modificar inscrição".
2. Observe a resposta.

**Item 5: semestre sem calendário**
1. Garanta que não existe `ClassSchedule` para um ano/semestre.
2. Como aluno, abra esse período no fluxo de inscrição (`StudentEnrollmentController#_redirect_semester`).

**Item 6: data impossível na simulação**
1. Abra a simulação de notificação.
2. Informe uma data de consulta impossível.

## Comportamento observado

1. A página da matrícula fica inacessível para o aluno.
   - A tela do admin abre normalmente, o que explica o erro ter passado despercebido.
   - Foram atingidas duas matrículas, em duas instâncias.
2. O Rails trata `InvalidAuthenticityToken` como 422 e exibe a página estática.
   - Essa página fala em *falta de permissão*, o que descreve errado uma sessão expirada.
   - No formulário de inscrição em disciplinas, o aluno perde todo o preenchimento.
   - Cada ocorrência gera um e-mail de erro, o que lota a caixa.
3. O candidato recebe "não pode ficar em branco" num campo que está preenchido na frente dele.
   - O servidor valida o input escondido, que só era remontado no evento `change` dos campos visíveis.
   - A validação do cliente passa, porque o campo visível está de fato preenchido.
4. Ocorre `ParameterMissing` e o candidato recebe a página crua de 400 do Rails, sem explicação.
5. Ocorre `CanCan::AccessDenied`. O aluno, seguindo um caminho legítimo, recebe uma acusação de tentativa de acesso indevido.
6. Ocorre `Date::Error` e a página cai, em vez de mostrar um aviso.

## Comportamento esperado

1. A página da matrícula abre para o aluno, como já abre para o admin.
2. Uma sessão expirada não deve aparecer como erro de permissão.
   - O usuário deve ser informado do motivo real.
   - Uma simples expiração não deve gerar notificação por e-mail.
   - Um token inválido com sessão ainda ativa continua merecendo notificação, pois pode ser defeito, formulário adulterado ou ataque.
3. O valor que o usuário vê preenchido deve ser aceito pelo servidor, seja qual for a forma como foi inserido.
4. O candidato deve voltar à inscrição com uma explicação, em vez de ver a página de 400.
5. O aluno deve receber uma mensagem informativa de que o semestre ainda não está disponível. A falta real de permissão continua sendo negada.
6. O usuário deve receber um aviso sobre a data inválida, e a página não deve cair.

## Stack trace / saída de erro

Não há stack traces na issue original. Ela cita apenas estes erros e status:

| Item | Erro / status |
|------|---------------|
| 1 | `NameError`, por referência a um local de parcial que não foi passado |
| 2 | `ActionController::InvalidAuthenticityToken`, resposta 422 |
| 4 | `ActionController::ParameterMissing`, resposta 400 |
| 5 | `CanCan::AccessDenied` |
| 6 | `Date::Error` |

## Caso de teste

A issue informa que:
- cada item tem um teste de regressão que falha antes da correção e passa depois;
- a suíte completa está verde.

O código dos testes não foi incluído. Cenários descritos:

- **Item 1:** aluno abre a própria matrícula, desligada, com banca e sem data de defesa.
- **Item 2:** envio de formulário com token vencido e sessão vazia; envio com sessão preenchida e token que não confere; requisição não-navegacional.
- **Item 3:** valor inserido sem disparar `change`. Testes que devem passar antes e depois: digitação, autocomplete e submissão por Enter, nos três widgets.
- **Item 4:** PUT sem `record` em `create` e em `update`.
- **Item 5:** semestre sem `ClassSchedule`. Teste que deve passar antes e depois: acesso à matrícula de outro aluno continua barrado.
- **Item 6:** data impossível na simulação de notificação.

## Exemplo de código

A issue não traz trechos de código completos. Pontos citados:

- **Item 1:** `app/views/enrollments/_show_defense_committee_table.html.erb` usa o local `dismissal_date`, mas só um dos dois chamadores o passa.
  - Em Rails, um local de parcial que não foi passado não vale `nil`: ele simplesmente não existe.
  - Por causa do curto-circuito do `||`, a referência só é avaliada quando a data de defesa é nula.
- **Item 4:** `Admissions::ApplyController` chama `params.require(:record)` sem nenhum tratamento.
- **Item 5:** `StudentEnrollmentController#_redirect_semester` levanta `CanCan::AccessDenied` quando não existe `ClassSchedule` para o ano/semestre pedido.
- **Item 6:** o `strptime` aceita mais de um formato desde a #530, mas uma data impossível ainda gera `Date::Error`.

## Versão e ambiente

- Produção, com erros registrados em julho de 2026 em múltiplas instâncias do SAPOS (aplicação Rails).
- Versões não informadas na issue original.