# Spec: Aplicar a expiração do documento (`Report#expires_at`) na decisão de download

## Objetivo

Hoje um documento gerado pelo SAPOS (`Report`) só deixa de ser baixável depois que a rotina diária `maintenance:remove_expired_reports` zera `carrierwave_file_id`. Entre o vencimento e a próxima execução do cron, que pode levar até um dia, o PDF continua sendo servido, embora o próprio rodapé diga "válido até DD/MM/AAAA".

O objetivo é que a regra de negócio "documento vencido não é servido" fique na decisão de download (`ReportsController#cant_download?`), e não na rotina de limpeza. A partir disso:

- Um documento vencido passa a exibir a tela `reports/expired_or_invalid_report`, já criada na #510, assim que vence, sem depender do cron.
- A rotina `maintenance:remove_expired_reports` passa a ser só limpeza de armazenamento.
- O que o PDF afirma e o que o sistema faz deixam de divergir.

**Usuários afetados:** quem baixa documentos gerados pelo SAPOS. Quem exatamente pode baixar (usuários autenticados, terceiros com link ou código de validação) não está informado na issue.

**Relação com outras issues:** complementa a #510, que definiu a tela de documento expirado ou invalidado. Esta issue trata da **condição** que decide quando mostrar essa tela.

**Histórias de usuário / critérios de aceitação:**

- Como usuário, ao tentar baixar um documento cujo `expires_at` já passou, vejo a tela de documento expirado ou invalidado, mesmo que o arquivo ainda exista no armazenamento.
- Como usuário, ao baixar um documento dentro da validade, recebo o arquivo normalmente.
- Como usuário, ao tentar baixar um documento invalidado manualmente (`Report#invalidate!`) ou sem arquivo, continuo vendo a mesma tela de hoje.

## Premissas

1. A aplicação é Rails, inferido de `ReportsController`, `lib/tasks/maintenance.rake`, views em `reports/` e da menção ao "404 do Rails".
2. O arquivo é gerenciado via CarrierWave, inferido de `carrierwave_file` e `carrierwave_file_id`. A biblioteca e a versão exatas são desconhecidas.
3. O framework de testes é RSpec, inferido do pedido de "spec de request". A existência e a localização de `spec/requests/` não foram confirmadas.
4. `cant_download?` é o único ponto de decisão que leva à view `reports/expired_or_invalid_report`. Todo caminho de download de `Report` passa por ele.
5. A view `reports/expired_or_invalid_report` já trata os casos expirado e invalidado e não precisa ser alterada.
6. Um `Report` com `expires_at` nulo é considerado sem expiração e continua baixável se tiver arquivo. Isso precisa ser confirmado (ver Perguntas em Aberto).
7. Um documento é considerado vencido quando o instante atual é posterior a `expires_at`. A semântica exata da fronteira está em aberto.
8. A rotina `maintenance:remove_expired_reports` continua existindo e continua apagando arquivos de documentos vencidos. Só deixa de ser a responsável pela regra de negócio.
9. A listagem de documentos, que exibe `expires_at`, está fora do escopo.

## Stack Tecnológica

- Ruby on Rails (premissa). Versão: Não informado na issue original.
- CarrierWave (premissa). Versão: Não informado na issue original.
- RSpec para specs de request (premissa). Versão: Não informado na issue original.
- Ferramenta de controle de tempo nos testes (por exemplo, helpers de tempo do Rails): Não informado na issue original.

## Comandos

Não informado na issue original.

- Build: desconhecido
- Testes: desconhecido (presumivelmente RSpec, mas o comando exato não está na issue)
- Lint: desconhecido
- Dev: desconhecido
- Rotina de manutenção: a task `maintenance:remove_expired_reports` é citada, mas a forma exata de invocação (por exemplo, via `rake` ou `bin/rails`) e o agendamento do cron são desconhecidos.

## Estrutura do Projeto

Arquivos e artefatos citados na issue:

```
ReportsController                          → contém #cant_download? (caminho do arquivo não informado)
Report (model)                             → expires_at, carrierwave_file, carrierwave_file_id, #invalidate!
reports/expired_or_invalid_report          → view exibida para documento expirado/invalidado (#510)
lib/tasks/maintenance.rake                 → task maintenance:remove_expired_reports
```

Local dos specs de request: desconhecido. Presumivelmente um diretório de specs do RSpec, mas não confirmado.

## Estilo de Código

Único trecho disponível na issue, que mostra o estado atual:

```ruby
def cant_download?(record)
  record.carrierwave_file.blank?
end
```

Convenções gerais de nomenclatura, formatação e linter: Não informado na issue original.

## Estratégia de Testes

- **Nível:** spec de request, que hoje não existe, cobrindo o fluxo de download de `Report`.
- **Cenários mínimos, pedidos na issue:**
  - Documento vencido (`expires_at` no passado) **com arquivo presente**: exibe `reports/expired_or_invalid_report` e não serve o arquivo.
  - Documento não vencido (`expires_at` no futuro) com arquivo presente: serve o arquivo.
- **Cenários recomendados, como regressão e fronteira:**
  - Documento invalidado via `Report#invalidate!`: continua exibindo a tela.
  - Documento sem arquivo (`carrierwave_file` em branco): continua exibindo a tela.
  - Documento com `expires_at` nulo: comportamento conforme a resposta às Perguntas em Aberto.
  - Fronteira de vencimento, no último dia de validade e no instante logo após: conforme a semântica definida.
- **Controle de tempo:** os testes devem fixar o "agora" para não ficarem instáveis. A ferramenta é desconhecida.
- **Cobertura mínima exigida:** Não informado na issue original.

## Limites

- **Sempre:**
  - Manter a decisão de download centralizada em `cant_download?`.
  - Manter o comportamento atual para documentos invalidados e documentos sem arquivo.
  - Rodar a suíte de testes antes de commitar.
- **Perguntar antes:**
  - Alterar a semântica ou o tipo de `expires_at`, incluindo migrações.
  - Mudar o comportamento da rotina `maintenance:remove_expired_reports` além do necessário para alinhá-la à mesma regra.
  - Alterar a view `reports/expired_or_invalid_report` ou o status HTTP da resposta.
  - Adicionar dependências, por exemplo para controle de tempo nos testes.
- **Nunca:**
  - Servir um documento cujo `expires_at` já passou.
  - Remover a rotina de manutenção sem aprovação.
  - Remover ou desativar testes existentes que falhem sem aprovação.

## Critérios de Sucesso

1. Uma requisição de download de um `Report` com `expires_at` no passado e `carrierwave_file` presente exibe `reports/expired_or_invalid_report` e não entrega o arquivo, sem qualquer execução do cron.
2. Uma requisição de download de um `Report` com `expires_at` no futuro e arquivo presente entrega o arquivo normalmente.
3. Documentos invalidados (`Report#invalidate!`) e documentos sem arquivo continuam exibindo a mesma tela de hoje.
4. A fronteira de vencimento é coerente com o texto impresso no PDF ("válido até DD/MM/AAAA"), conforme a semântica definida nas Perguntas em Aberto.
5. A rotina `maintenance:remove_expired_reports` continua removendo arquivos vencidos, e sua definição de "vencido" é a mesma usada em `cant_download?`.
6. Existe uma spec de request cobrindo pelo menos os casos vencido e não vencido, e ela passa.
7. A suíte de testes existente continua passando.

## Perguntas em Aberto

1. **Semântica da fronteira:** "válido até DD/MM/AAAA" inclui o dia inteiro? `expires_at` é data ou data e hora? O documento deve vencer em `expires_at` exato ou só no fim do dia exibido?
2. **Fuso horário:** a comparação deve usar o fuso configurado da aplicação? O fuso do PDF é o mesmo usado na comparação?
3. **`expires_at` nulo:** existem documentos sem data de expiração? Se existirem, devem ser sempre baixáveis?
4. **Consistência com o cron:** a rotina usa hoje a mesma condição de vencimento? Se a condição for diferente, deve ser alinhada nesta issue ou em outra?
5. **Outros caminhos de download:** há outros pontos que servem o arquivo de `Report` (por exemplo, validação pública por código ou QR code, API) sem passar por `cant_download?`?
6. **Status HTTP:** qual status a tela `reports/expired_or_invalid_report` deve retornar, por exemplo 200, 404 ou 410? A spec de request deve verificar o status ou só o template renderizado?
7. **Listagem:** a listagem deve passar a sinalizar visualmente documentos vencidos, ou isso fica fora do escopo?
8. **Ambiente de testes:** qual o comando para rodar os testes, onde ficam as specs de request e qual ferramenta de controle de tempo já é usada no projeto?