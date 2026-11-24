# Spec: Correção do erro no envio de e-mails após atualização do Rails

## Objetivo

Restaurar o envio de e-mails da aplicação, que passou a falhar. A suspeita é de que a falha tenha começado após uma atualização do Rails.

**Usuários afetados:** os destinatários dos e-mails da aplicação e quem depende desse envio (por exemplo, para confirmação de conta, recuperação de senha ou notificações). Quais fluxos usam e-mail não foi informado na issue original.

**Critérios de aceitação (proposta, pendente de validação):**
- Os e-mails que falham hoje voltam a ser enviados sem exceção.
- A causa raiz é identificada e registrada, confirmando ou descartando a relação com a atualização do Rails.
- Existe um teste automatizado que reproduz o erro antes da correção e passa depois dela.
- Nenhum outro fluxo de e-mail regride.

## Premissas

1. A aplicação usa Action Mailer, o mecanismo padrão de e-mail do Rails.
2. O erro aparece no momento do envio e não é um problema de entrega na ponta do provedor, como spam ou bounce. A frase "dando erro ao serem enviados" sugere isso, mas não confirma.
3. A atualização do Rails foi a mudança mais recente e relevante antes do início do erro. A issue diz que a relação é "provável", portanto é uma hipótese a validar.
4. O problema afeta todos os e-mails, ou ao menos vários tipos, e não um único mailer. A issue não deixa isso claro.
5. O envio pode ser assíncrono (`deliver_later` via Active Job). Nesse caso, a mudança de versão também pode afetar a fila ou a serialização dos jobs.
6. O objetivo é corrigir a aplicação para funcionar com a nova versão do Rails, e não reverter a atualização. Isso precisa de confirmação.

## Stack Tecnológica

- **Framework:** Ruby on Rails. Versão anterior e versão nova não informadas na issue original.
- **Versão do Ruby:** desconhecida.
- **Envio de e-mail:** provavelmente Action Mailer. Método de entrega (SMTP, Sendmail, serviço/API de terceiros) desconhecido.
- **Fila / Active Job adapter:** desconhecido.
- **Gems relacionadas a e-mail** (ex.: `mail`, `net-smtp`, gems de provedor): desconhecidas.

## Comandos

Não informado na issue original.

- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Não informado na issue original. Os caminhos dos mailers, templates, configurações de ambiente e testes não foram fornecidos.

## Estilo de Código

Não informado na issue original.

## Estratégia de Testes

O framework de testes (Minitest ou RSpec) não foi informado na issue original. Diretrizes propostas:

- **Reprodução:** escrever primeiro um teste que reproduza a falha de envio na versão atual do Rails.
- **Unitário/mailer:** cobrir os mailers afetados, verificando que a mensagem é gerada com destinatário, assunto e corpo corretos.
- **Integração:** se o envio for assíncrono, verificar que o job de entrega é enfileirado e executado sem erro.
- **Regressão:** executar a suíte existente de mailers e jobs.
- **Verificação manual:** validar o envio real em staging ou ambiente equivalente, se existir (não informado).
- **Meta de cobertura:** desconhecida.

## Limites

- **Sempre:**
  - Reproduzir o erro com um teste antes de corrigir.
  - Rodar a suíte de testes antes de commitar.
  - Registrar a causa raiz na issue ou no PR.
- **Perguntar antes:**
  - Reverter ou fazer downgrade do Rails ou de qualquer gem.
  - Adicionar, remover ou fixar versões de dependências.
  - Alterar credenciais, configuração do provedor de e-mail ou configurações de produção.
  - Alterar a configuração de filas ou do Active Job.
- **Nunca:**
  - Commitar credenciais SMTP ou chaves de API.
  - Desativar ou silenciar erros de envio (ex.: `raise_delivery_errors = false`) como "correção".
  - Remover ou pular testes que falham sem aprovação.
  - Enviar e-mails reais para usuários durante testes.

## Critérios de Sucesso

- [ ] A mensagem de erro e o stack trace originais foram coletados e documentados.
- [ ] A causa raiz foi identificada, e a relação com a atualização do Rails foi confirmada ou descartada.
- [ ] Um teste automatizado reproduz a falha e passa após a correção.
- [ ] Todos os tipos de e-mail afetados voltam a ser enviados sem exceção no ambiente de teste.
- [ ] Se o envio for assíncrono, os jobs de entrega são processados sem erro.
- [ ] A suíte de testes completa passa sem novas falhas.
- [ ] O envio foi validado em um ambiente que não seja de desenvolvimento, se existir.

## Perguntas em Aberto

1. **Qual é a mensagem de erro exata e o stack trace?** Esta é a informação mais importante para o diagnóstico.
2. De qual versão para qual versão o Rails foi atualizado? As versões do Ruby e de outras gems também mudaram?
3. Todos os e-mails falham ou apenas alguns (mailers ou templates específicos)?
4. Em quais ambientes o erro ocorre: desenvolvimento, staging, produção?
5. Qual método de entrega é usado (SMTP, Sendmail, serviço/API de terceiros)? A configuração ou as credenciais mudaram junto com a atualização?
6. O envio é síncrono (`deliver_now`) ou assíncrono (`deliver_later`)? Qual adapter de fila é usado?
7. Quando o erro começou? A data coincide com o deploy da atualização do Rails?
8. Existem testes de mailer na aplicação hoje? Eles passam ou falham após a atualização?
9. Reverter a atualização do Rails é uma opção aceitável, ou a correção deve manter a nova versão?
10. Existe algum workaround em uso ou um impacto de negócio que defina a urgência?
11. Quais são os comandos de build, teste e lint, e qual é a estrutura de diretórios do projeto?