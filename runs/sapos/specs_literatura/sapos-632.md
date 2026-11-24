## Resumo

O anexo de boletim (PDF) gerado pela rake task de notificações sai **vazio (0 bytes)**. O mesmo anexo gerado pelo controller sai correto. O commit que fechou a #547 (`5b08d32a`, "Fix the grades_report generation for notifications") alterou apenas estes arquivos:

- `app/controllers/notifications_controller.rb`
- `app/controllers/concerns/shared_pdf_concern.rb`
- a view do boletim

O arquivo `lib/tasks/maintenance.rake` não foi alterado e mantém a chamada antiga, com um argumento só. Com isso, as duas cópias de `prepare_attachments` divergiram.

**Impacto:** não há impacto em produção. Uma versão anterior desta issue afirmava o contrário, mas isso estava incorreto. A funcionalidade não é usada em produção desde o início de 2025, quando os alunos passaram a gerar o boletim com QR Code pelo próprio SAPOS.

**Histórico do sintoma "anexo de boletim não enviado":**
- **#333** (2020): criou o envio de notificação com boletim anexado.
- **#400** (2022): registrou o anexo não sendo enviado. Corrigido na 5.0.8.
- **#547** (2025): registrou o mesmo sintoma após a mudança no mecanismo de geração de boletim. Fechada na 7.15.5.

**Outros fatos registrados na issue:**
- Durante a #547, o commit `93141771` removeu a coluna `has_grades_report_pdf_attachment`. O commit `0db4e774` reverteu essa remoção.
- A coluna e a opção continuam existindo na interface.
- A issue original também pede uma decisão sobre o futuro dessa opção. Essa discussão não é reproduzida aqui.

## Passos para reproduzir

1. Configure uma notificação com a opção de anexar boletim ativada (coluna `has_grades_report_pdf_attachment`).
2. Execute a notificação pelo controller, via `execute_now`, que usa o `prepare_attachments` do controller.
3. Com a mesma notificação e os mesmos dados, execute o caminho da rake task em `lib/tasks/maintenance.rake`, que é o caminho executado pelo cron e usa o `prepare_attachments` da rake task.
4. Compare o tamanho do anexo de boletim gerado em cada caminho.

## Comportamento observado

| Caminho | Anexo |
|---|---|
| `prepare_attachments` do controller (usado por `execute_now`) | PDF real, ~48 KB |
| `prepare_attachments` da rake task (executado pelo cron) | **0 bytes** |

Segundo a issue, a causa é a seguinte:
- `SharedPdfConcern#render_enrollments_grades_report_pdf` depende de um contexto de renderização de controller.
- Fora desse contexto, `render_to_string` devolve `nil` sem levantar exceção.
- Por isso a falha é silenciosa.

## Comportamento esperado

Os dois caminhos deveriam ter o mesmo comportamento para a mesma notificação e os mesmos dados. A rake task executada pelo cron não deveria produzir um anexo vazio sem nenhum aviso.

## Stack trace / saída de erro

Não há stack trace. A falha é silenciosa: `render_to_string` devolve `nil` fora do contexto de controller, sem levantar exceção.

## Caso de teste

`spec/features/notifications_spec.rb` contém um exemplo que fixa o comportamento atual (anexo vazio gerado pela rake task). Segundo a issue:
- o exemplo falha de propósito quando o caminho da rake task for corrigido;
- ele deve ser removido junto se a funcionalidade for retirada.

O código desse exemplo não consta na issue original.

## Exemplo de código

Chamada no controller após o commit `5b08d32a`:

```ruby
render_enrollments_grades_report_pdf(enrollment, filename, signature_type, watermark: true)
```

A chamada antiga, de um argumento só, que permanece em `lib/tasks/maintenance.rake`, não foi transcrita na issue original.

## Versão e ambiente

- Correção da #547 incluída na versão **7.15.5**, que não alcançou a rake task.
- A correção anterior do mesmo sintoma (#400) saiu na versão 5.0.8.
- Arquivos envolvidos:
  - `app/controllers/notifications_controller.rb`
  - `app/controllers/concerns/shared_pdf_concern.rb`
  - `lib/tasks/maintenance.rake`
  - `spec/features/notifications_spec.rb`
- Commits citados: `5b08d32a`, `93141771` e `0db4e774`.
- As versões de Ruby, Rails e sistema operacional não foram informadas na issue original.