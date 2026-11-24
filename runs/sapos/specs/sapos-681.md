# Spec: Cobertura por specs da lógica do processo seletivo (admissions)

## Objetivo

Proteger com specs a lógica de produto do processo seletivo que hoje quase não é executada pela suíte. Os quatro caminhos de negócio a cobrir são:

- consolidação de fase e troca de fase dos candidatos;
- cálculo de ranking;
- geração dos relatórios do processo (grupos por fase, carta, ranking);
- validação dos formulários preenchidos e avaliação de condição sobre eles.

**Por quê:** essa lógica não é superfície de gem. Uma campanha de atualização de dependências não a exercita, e um defeito ali só aparece quando o processo seletivo roda de fato.

**Quem se beneficia:** mantenedores do sistema. Eles passam a poder alterar ou atualizar o código de admissions com uma rede de regressão.

**Situação medida (antes):** com `bundle exec rspec` e relatório em `coverage/index.html`, a cobertura de linhas está em 82%. São 1971 linhas não executadas em cerca de 11 mil relevantes.

| diretório | não cobertas | relevantes |
|---|---|---|
| `app/models` | 953 | 4987 |
| `app/controllers` | 522 | 3500 |
| `app/helpers` | 364 | 2018 |
| `lib/tasks` | 53 | 111 |

**Arquivos-alvo (não cobertas / relevantes):**

| arquivo | antes |
|---|---|
| `app/models/admissions/admission_application.rb` | 155 / 337 |
| `app/controllers/admissions/admission_processes_controller.rb` | 142 / 230 |
| `app/controllers/admissions/admission_applications_controller.rb` | 133 / 310 |
| `app/models/admissions/admission_phase.rb` | 82 / 109 |
| `app/models/admissions/admission_report_config.rb` | 65 / 109 |
| `app/models/admissions/admission_report_group_phase.rb` | 61 / 85 |
| `app/models/admissions/filled_form.rb` | 48 / 91 |
| `app/controllers/admissions/admissions_controller.rb` | 47 / 88 |
| `app/models/admissions/form_condition.rb` | 43 / 110 |
| `app/models/admissions/admission_report_group_letter.rb` | 42 / 49 |
| `app/models/admissions/filled_form_field.rb` | 41 / 216 |
| `app/helpers/admissions/admission_processes_pdf_helper.rb` | 41 / 93 |

**Histórias / critérios de aceitação por caminho, na ordem de peso do descoberto:**

1. **`consolidate_phase`**
   - Os candidatos aprovados, reprovados, sem comitê e com erro são tratados conforme o comportamento atual.
   - A passagem dos candidatos para a fase seguinte é verificada.
2. **Ranking e consolidação por candidato**
   - `calculate_ranking` é exercitado com um `RankingConfig` real, não um dublê.
   - `AdmissionApplication#consolidate_phase!` é exercitado diretamente.
3. **Relatórios do processo**
   - `AdmissionReportConfig` e os `AdmissionReportGroup*` (fase, carta, ranking) são protegidos.
   - O formato preferido é golden-master em `spec/requests/goldens/`, como os demais PDFs e XLSX.
4. **Formulários preenchidos**
   - A validação de `FilledForm` / `FilledFormField` é coberta.
   - A avaliação de `FormCondition` sobre um formulário preenchido é coberta.

**Fora de escopo, já feito na campanha de 2026-09-10:**

- a ação `duplicate` por GET nos seis controllers de admissions;
- os dois `rescue` de `admission_processes_controller.rb` que chamam `ExceptionNotifier.notify_exception`;
- a ampliação dos goldens do histórico e do boletim (`enrollments_pdf_helper.rb`).

## Premissas

1. O projeto é uma aplicação Ruby on Rails testada com RSpec. Isso é inferido da estrutura `app/models`, `app/controllers`, `app/helpers`, `lib/tasks` e do comando `bundle exec rspec`.
2. A cobertura é gerada automaticamente ao rodar a suíte inteira, provavelmente via SimpleCov. A ferramenta e a configuração exatas não são informadas.
3. `consolidate_phase` e `calculate_ranking` são ações de `admission_processes_controller.rb`. Por isso devem ser cobertas por request specs em `spec/requests/admissions/`. As regras de modelo vão em `spec/models/admissions/`.
4. Os specs devem **caracterizar o comportamento atual**. O objetivo é cobertura e proteção contra regressão, não mudança de comportamento.
5. Já existe infraestrutura de golden-master em `spec/requests/goldens/` para PDF e XLSX, reutilizável para os relatórios do processo.
6. Há factories ou fixtures para os modelos de admissions, ou elas podem ser criadas dentro de `spec/`.
7. A entrega pode ser feita em mais de um PR, um por caminho de negócio, na ordem sugerida.

## Stack Tecnológica

- Ruby / Rails / RSpec. As versões não são informadas na issue.
- A gem `ExceptionNotifier` está presente.
- A ferramenta de cobertura não é nomeada (presumivelmente SimpleCov).
- A biblioteca de geração de PDF/XLSX dos goldens não é informada na issue.

## Comandos

- **Testes + cobertura:** `bundle exec rspec` (suíte inteira; relatório em `coverage/index.html`).
- **Rodar um spec isolado:** não informado na issue original.
- **Regenerar/atualizar goldens:** não informado na issue original.
- **Lint:** não informado na issue original.

## Estrutura do Projeto

```
app/models/admissions/        → Modelos do processo seletivo (alvo)
app/controllers/admissions/   → Controllers do processo seletivo (alvo)
app/helpers/admissions/       → Helpers, incl. admission_processes_pdf_helper.rb (alvo)
spec/requests/admissions/     → Request specs de admissions (destino dos novos specs)
spec/models/admissions/       → Model specs de admissions (destino dos novos specs)
spec/requests/goldens/        → Golden-masters de PDF/XLSX (destino dos relatórios)
coverage/index.html           → Relatório de cobertura
```

## Estilo de Código

Não informado na issue original.

Convenção indicada pela issue: um arquivo de spec por caminho de negócio.

## Estratégia de Testes

**Framework:** RSpec.

**Níveis de teste por preocupação:**

| Preocupação | Nível | Local |
|---|---|---|
| `consolidate_phase`, `calculate_ranking`: fluxo HTTP, troca de fase | Request spec | `spec/requests/admissions/` |
| `AdmissionApplication#consolidate_phase!`, `AdmissionPhase`, `RankingConfig` | Model spec | `spec/models/admissions/` |
| `AdmissionReportConfig`, `AdmissionReportGroup*`, `admission_processes_pdf_helper.rb` | Golden-master (PDF/XLSX) | `spec/requests/goldens/` |
| `FilledForm`, `FilledFormField`, `FormCondition` | Model spec | `spec/models/admissions/` |

**Medição:**

- Rodar `bundle exec rspec` com a suíte inteira **antes** e **depois**.
- Registrar na issue, com o mesmo relatório:
  - a cobertura total;
  - as linhas não cobertas por diretório;
  - as linhas não cobertas em cada arquivo-alvo.

**Dados:** usar objetos reais onde a issue pede, em especial um `RankingConfig` real em vez de dublê.

## Limites

**Sempre:**
- Rodar a suíte inteira antes de cada commit.
- Medir a cobertura antes e depois com o mesmo comando e relatório.
- Manter um spec por caminho de negócio.
- Seguir o padrão golden-master existente para relatórios.

**Perguntar antes:**
- Alterar qualquer código em `app/` ou `lib/`. Por exemplo, quando um spec revelar defeito ou código não testável sem refatoração.
- Adicionar dependências ou gems de teste.
- Alterar a configuração de cobertura.
- Regenerar goldens já existentes, que não sejam os novos desta issue.

**Nunca:**
- Ajustar um spec para "passar" escondendo um defeito encontrado. Registrar o defeito e perguntar.
- Remover ou enfraquecer specs existentes.
- Alterar os specs e goldens da campanha de 2026-09-10 (`duplicate`, `rescue` com `ExceptionNotifier`, histórico/boletim).

## Critérios de Sucesso

1. Existe ao menos um spec para cada um dos quatro caminhos de negócio, nos diretórios indicados.
2. `consolidate_phase` tem cenários explícitos para os seguintes casos:
   - candidato aprovado;
   - candidato reprovado;
   - candidato sem comitê;
   - candidato com erro;
   - passagem dos candidatos para a fase seguinte.
3. `calculate_ranking` é exercitado com um `RankingConfig` real.
4. `AdmissionApplication#consolidate_phase!` é exercitado diretamente.
5. Os relatórios do processo (grupos por fase, carta, ranking) têm golden-master em `spec/requests/goldens/`, ou justificativa registrada para outro formato.
6. `FilledForm` / `FilledFormField` (validação) e `FormCondition` (avaliação sobre formulário preenchido) têm specs.
7. A suíte inteira passa com `bundle exec rspec`.
8. A issue é fechada com a tabela antes/depois:
   - cobertura total;
   - linhas não cobertas por diretório;
   - linhas não cobertas em cada um dos 12 arquivos-alvo.
9. O número de linhas não cobertas diminui em cada arquivo-alvo. A meta numérica está pendente (ver Questões em Aberto).

## Questões em Aberto

1. **Meta de cobertura.** Há uma meta para fechar a issue? Por exemplo: cobertura total ≥ X%, um teto de linhas descobertas por arquivo-alvo, ou basta qualquer redução medida?
2. **Defeitos encontrados.** Se um spec revelar defeito na lógica atual, ele é corrigido nesta issue, aberto como issue separada, ou marcado como `pending`?
3. **Ações de controller.** `consolidate_phase` e `calculate_ranking` são de fato ações de `admission_processes_controller.rb`? Quais outras ações de `admission_applications_controller.rb` (133 linhas descobertas) e `admissions_controller.rb` (47) entram no escopo? Os quatro itens sugeridos não as mencionam explicitamente.
4. **Golden-master.** Qual o procedimento para gerar e aprovar novos goldens? Como lidar com conteúdo não determinístico (datas, IDs) nos PDFs/XLSX dos relatórios?
5. **Formato de cada relatório.** O relatório de ranking e o de grupos por fase saem em PDF, XLSX ou ambos?
6. **Dados de teste.** Existem factories para `AdmissionProcess`, `AdmissionPhase`, `AdmissionApplication`, `RankingConfig`, `FilledForm`, `FormCondition` e `AdmissionReportConfig`? Ou será preciso criá-las?
7. **`lib/tasks`.** As 53 linhas não cobertas de `lib/tasks` estão fora de escopo desta issue?
8. **Divisão da entrega.** A issue reúne quatro caminhos testáveis de forma independente. Prefere uma entrega única ou um PR/issue por caminho, na ordem sugerida?
9. **Ferramenta de cobertura.** Qual ferramenta gera `coverage/index.html`? Ela mede cobertura de branches além de linhas? Isso deve entrar no relatório antes/depois?