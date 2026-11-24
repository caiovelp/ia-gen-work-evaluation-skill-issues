# Spec: Anexo de boletim em notificações — remover a opção ou corrigir a rake task (seguimento da #547)

## Objetivo

A correção da #547 (commit `5b08d32a`, versão 7.15.5) alcançou apenas o caminho do controller. A rake task executada pelo cron ainda tem uma cópia antiga da lógica e gera **anexo de boletim com 0 bytes, sem levantar erro**. O defeito é silencioso.

O objetivo é eliminar essa divergência com uma decisão explícita sobre o futuro da opção "anexar boletim" nas notificações. Há dois caminhos:

- **Opção 1 (recomendada na issue): remover a funcionalidade.** Isso inclui a coluna `has_grades_report_pdf_attachment`, o campo no formulário e o ramo de anexo nas duas cópias de `prepare_attachments`. A justificativa é a decisão de produto já tomada: desde o início de 2025, os alunos geram o boletim com QR Code pelo próprio SAPOS.
- **Opção 2: corrigir a rake task.** A rake task passaria a renderizar o boletim com contexto de renderização, por exemplo via `ApplicationController.renderer`. Também seria preciso definir explicitamente o formato do documento enviado por e-mail.

**Usuários afetados:** administradores e secretaria que configuram notificações no SAPOS. A issue informa que a funcionalidade não é usada em produção desde o início de 2025, então não há impacto conhecido em usuários finais.

**Sucesso:** não existem mais duas cópias divergentes do ramo de anexo de boletim. Ou a funcionalidade deixa de existir de forma completa e consistente, ou os dois caminhos de envio (`execute_now` e cron) produzem o mesmo anexo válido.

### Contexto factual (da issue)

| Item | Detalhe |
|---|---|
| #333 (2020) | Criou o envio de notificação com boletim anexado |
| #400 (2022) | Anexo não enviado; corrigido na 5.0.8 |
| #547 (2025) | Mesmo sintoma após a mudança no mecanismo de geração; fechada na 7.15.5 |
| `5b08d32a` | Alterou `app/controllers/notifications_controller.rb`, `app/controllers/concerns/shared_pdf_concern.rb` e a view do boletim. A nova chamada é `render_enrollments_grades_report_pdf(enrollment, filename, signature_type, watermark: true)` |
| `lib/tasks/maintenance.rake` | Não foi alterado. Mantém a chamada antiga, de um argumento |
| `93141771` | Removeu a coluna `has_grades_report_pdf_attachment` durante a #547 |
| `0db4e774` | Reverteu `93141771`. Motivo não informado |
| Causa da falha silenciosa | `SharedPdfConcern#render_enrollments_grades_report_pdf` depende do contexto de controller. Fora dele, `render_to_string` devolve `nil` |

Medição registrada na issue (mesma notificação, mesmos dados):

| Caminho | Anexo |
|---|---|
| `prepare_attachments` do controller (`execute_now`) | PDF real, ~48 KB |
| `prepare_attachments` da rake task (cron) | 0 bytes |

## Premissas

1. A decisão padrão é a **Opção 1 (remover)**, por ser a recomendada na issue e coerente com a decisão de produto. A Opção 2 só se aplica se um responsável pelo produto decidir manter a funcionalidade.
2. A afirmação "não é usada em produção desde o início de 2025" significa que nenhuma notificação ativa em produção depende hoje do anexo. Isso ainda precisa ser confirmado nos dados (ver Questões em aberto).
3. O projeto é uma aplicação Ruby on Rails, o que se deduz de `app/controllers`, `lib/tasks/*.rake`, `ApplicationController.renderer` e `concerns`. Os testes usam RSpec, o que se deduz de `spec/features/notifications_spec.rb`.
4. As "duas cópias" de `prepare_attachments` são exatamente as do controller e da rake task. Não há uma terceira cópia em jobs, mailers ou outros lugares.
5. Remover a opção exige uma migration de banco para a coluna `has_grades_report_pdf_attachment`.
6. O motivo da #547 para não gerar o boletim com QR Code no envio continua válido: evitar armazenar centenas de documentos assinados de uma vez. Por isso, na Opção 2, o documento enviado por e-mail **não** levaria QR Code / assinatura armazenada.
7. O restante do fluxo de notificações (outros anexos, envio de e-mail, agendamento pelo cron) deve continuar funcionando sem mudança de comportamento.

## Stack técnica

- Ruby on Rails (inferido; versões não informadas na issue).
- RSpec para testes (inferido por `spec/features/`).
- Gerador de PDF: não informado na issue original.

## Comandos

Não informado na issue original.

- Build: desconhecido
- Testes: desconhecido (provavelmente RSpec, mas o comando exato não aparece na issue)
- Lint: desconhecido
- Rake task executada pelo cron: nome da task desconhecido. Só se sabe que fica em `lib/tasks/maintenance.rake`.
- Migrations: desconhecido

## Estrutura do projeto

Apenas os caminhos citados na issue:

```
app/controllers/notifications_controller.rb        → prepare_attachments (caminho de execute_now)
app/controllers/concerns/shared_pdf_concern.rb     → render_enrollments_grades_report_pdf
lib/tasks/maintenance.rake                         → cópia de prepare_attachments usada pelo cron
spec/features/notifications_spec.rb                → exemplo que fixa o anexo vazio da rake task
```

Desconhecidos:
- Localização da view do boletim (alterada em `5b08d32a`).
- Formulário de notificação onde aparece o campo.
- Diretório de migrations e schema.

## Estilo de código

Não informado na issue original. A única referência de código é a chamada atual no controller:

```ruby
render_enrollments_grades_report_pdf(enrollment, filename, signature_type, watermark: true)
```

## Estratégia de testes

- **Exemplo existente** em `spec/features/notifications_spec.rb`: hoje fixa o anexo vazio gerado pela rake task e falha de propósito quando o caminho for corrigido.
  - **Opção 1:** remover esse exemplo junto com a funcionalidade. Os demais exemplos de notificação devem continuar passando.
  - **Opção 2:** substituir o exemplo por um que exija anexo não vazio e PDF válido gerado pelo caminho da rake task.
- **Teste de paridade (Opção 2):** a mesma notificação com os mesmos dados deve produzir anexos equivalentes pelo controller (`execute_now`) e pela rake task.
- **Regressão (Opção 1):**
  - Notificações sem anexo de boletim continuam sendo enviadas pelos dois caminhos.
  - O formulário de notificação não exibe mais a opção.
- **Falha silenciosa (Opção 2):** se a renderização retornar `nil` ou vazio, o sistema deve falhar ou registrar o erro de forma visível, em vez de anexar 0 bytes.
- Framework, local exato de testes unitários e meta de cobertura: não informados na issue original.

## Limites

- **Sempre:**
  - Tratar as duas cópias de `prepare_attachments` juntas. Nunca alterar uma sem a outra.
  - Manter o comportamento dos demais anexos e do envio de notificações.
  - Rodar a suíte de notificações antes de concluir.
  - Referenciar #547 e esta issue nos commits/PR.
- **Perguntar antes:**
  - Criar a migration que remove a coluna `has_grades_report_pdf_attachment`, que é uma mudança de schema.
  - Reaplicar ou contornar a remoção já revertida em `0db4e774`.
  - Unificar as duas cópias de `prepare_attachments` em um único ponto (refatoração além do escopo mínimo).
  - Adicionar dependências.
  - Mudar o formato do boletim enviado por e-mail: marca d'água, QR Code, assinatura.
- **Nunca:**
  - Gerar e armazenar em massa documentos assinados/com QR Code pelo envio de notificações.
  - Apagar o exemplo de `spec/features/notifications_spec.rb` sem substituí-lo, exceto na Opção 1, em que ele sai junto com a funcionalidade.
  - Deixar a falha silenciosa (anexo de 0 bytes) como comportamento aceito.

## Critérios de sucesso

**Comuns às duas opções:**
- Não existe mais nenhum caminho de envio de notificação que anexe um boletim de 0 bytes.
- O comportamento de anexo de boletim é idêntico entre `execute_now` e o cron, seja ausente nos dois ou presente e válido nos dois.
- Os testes de notificações passam, e o exemplo que fixava o anexo vazio foi removido ou substituído.

**Opção 1 — Remover:**
- A coluna `has_grades_report_pdf_attachment` não existe mais no schema, via migration reversível.
- O formulário de notificação não exibe o campo de anexar boletim.
- O ramo de anexo de boletim foi removido de `prepare_attachments` no controller e em `lib/tasks/maintenance.rake`.
- Não há referências restantes a `has_grades_report_pdf_attachment` no código, views ou testes.
- Notificações existentes que tinham a opção marcada continuam sendo enviadas, sem o anexo e sem erro.

**Opção 2 — Corrigir:**
- A rake task gera o boletim com contexto de renderização válido (por exemplo, `ApplicationController.renderer`).
- Para a mesma notificação e os mesmos dados, o anexo gerado pelo cron é um PDF válido e não vazio, equivalente ao do controller (~48 KB na medição da issue).
- O formato do documento enviado por e-mail está definido e documentado: com ou sem marca d'água, sem QR Code / sem armazenamento de documento assinado.
- Uma renderização que retorne `nil` ou vazio gera erro ou log visível, nunca um anexo de 0 bytes.

## Questões em aberto

1. **Decisão de produto:** confirmar a Opção 1 (remover) ou a Opção 2 (corrigir). Quem decide?
2. **Por que `93141771` foi revertido em `0db4e774`?** O motivo da reversão pode ser um impedimento que ainda vale, por exemplo dependência em outro lugar, dados existentes ou migration problemática.
3. **Uso real em produção:** existem notificações cadastradas, ativas ou agendadas, com `has_grades_report_pdf_attachment = true`? Se sim, o que fazer com elas na remoção: só ignorar o campo, avisar os responsáveis, desativar?
4. **Migration (Opção 1):** a coluna deve ser removida de fato ou apenas deixar de ser usada por um período, por segurança de deploy e rollback?
5. **Formato do e-mail (Opção 2):** o boletim enviado deve ter marca d'água (`watermark: true`, como no controller)? Qual `signature_type` deve ser usado no caminho do cron?
6. **Duplicação:** além desta correção, deve-se unificar as duas cópias de `prepare_attachments` em um único ponto compartilhado, ou isso fica para outra issue?
7. **Outras cópias:** há outros pontos (jobs, mailers, outras rake tasks) que chamam `render_enrollments_grades_report_pdf` fora de contexto de controller?
8. **Comandos e ambiente:** quais são os comandos de teste, lint e migration do projeto e o nome exato da rake task executada pelo cron? Não informado na issue original.
9. **Versão alvo:** em qual versão a mudança deve sair (após 7.15.5)?