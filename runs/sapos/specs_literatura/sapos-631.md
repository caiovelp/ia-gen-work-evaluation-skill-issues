## Resumo

Um documento gerado pelo SAPOS (`Report`) possui o campo `expires_at`. Esse campo aparece na listagem e é impresso no rodapé do PDF como "válido até DD/MM/AAAA". O download, porém, não verifica esse campo.

Hoje o documento só fica indisponível quando a rotina diária `maintenance:remove_expired_reports` (`lib/tasks/maintenance.rake`) roda e zera `carrierwave_file_id`. Por isso, entre o vencimento e a próxima execução da rotina, o documento vencido continua sendo servido normalmente. Essa janela é de até um dia.

O conteúdo do documento não muda nesse intervalo. O problema é a divergência entre o que o PDF afirma e o que o sistema faz. Além disso, a regra de negócio da expiração está na rotina de limpeza, e não na decisão de download.

Esta issue complementa a #510. A #510 definiu a tela de documento expirado (view `reports/expired_or_invalid_report`), que substitui o 404 do Rails. Esta issue trata da **condição** que decide quando essa tela é exibida.

## Passos para reproduzir

1. Gerar um documento (`Report`) no SAPOS com `expires_at` definido.
2. Aguardar até depois da data de `expires_at`, antes da próxima execução da rotina `maintenance:remove_expired_reports`.
3. Solicitar o download do documento.

Para comparar, o mesmo problema não acontece com a invalidação manual: `Report#invalidate!` apaga o arquivo na hora, e a tela de documento invalidado aparece imediatamente.

## Comportamento observado

- O documento vencido é servido normalmente, embora o próprio PDF declare que já venceu.
- A tela `reports/expired_or_invalid_report` só passa a aparecer depois que a rotina `maintenance:remove_expired_reports` roda e zera `carrierwave_file_id`. Só então `cant_download?` retorna verdadeiro.
- A janela em que o documento vencido continua disponível é de até um dia.

## Comportamento esperado

- Assim que `expires_at` for ultrapassado, o download deve ser recusado e a tela `reports/expired_or_invalid_report` deve ser exibida, sem depender da execução do cron.
- O que o sistema faz deve corresponder ao que o PDF declara ("válido até DD/MM/AAAA").

## Stack trace / saída de erro

Não informado na issue original.

## Caso de teste

A issue aponta que não existe hoje um spec de request para este cenário e sugere criar um que cubra os dois casos:

1. **Documento não vencido:** `Report` com `expires_at` no futuro e arquivo presente. O download deve ser servido normalmente.
2. **Documento vencido:** `Report` com `expires_at` no passado e arquivo ainda presente, ou seja, a rotina de manutenção ainda não rodou. O download não deve ser servido, e a tela `reports/expired_or_invalid_report` deve ser exibida.

## Exemplo de código

Implementação atual de `ReportsController#cant_download?`, que testa apenas se o arquivo está ausente:

```ruby
def cant_download?(record)
  record.carrierwave_file.blank?
end
```

Componentes relacionados citados na issue:
- `Report#expires_at`: data de validade exibida na listagem e no rodapé do PDF.
- `Report#invalidate!`: apaga o arquivo imediatamente.
- `maintenance:remove_expired_reports` (`lib/tasks/maintenance.rake`): rotina diária que zera `carrierwave_file_id` dos documentos vencidos.
- View `reports/expired_or_invalid_report`: tela introduzida na #510, que cobre os casos de documento expirado e invalidado.

## Versão e ambiente

Não informado na issue original.