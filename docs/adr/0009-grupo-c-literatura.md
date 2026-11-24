# 0009 — Grupo C: reescrita guiada pelos critérios da literatura, por tipo

Data: 2026-10-26 · Status: aceita

## Contexto
O Grupo A reescreveu todas as issues com o molde genérico da skill Spec-Driven Development (Objetivo, Comandos, Estrutura do projeto, Estilo de código, Testes, Limites, Critérios de sucesso). Esse molde não segue os critérios de qualidade de relato da literatura, nem distingue bug de feature. O Caio pediu uma reescrita que siga a referência de cada tipo.

## Decisão
Novo braço **Grupo C (literatura)**, ao lado de A (Spec-Driven) e B (original), só para issues classificadas como bug ou feature (ADR 0008).
- **Bug — Bettenburg et al. (2008), §3.1:** "the most widely used items across projects are steps to reproduce, observed and expected behavior, stack traces, and test cases". Seções: Summary, Steps to reproduce, Observed behavior, Expected behavior, Stack trace / error output, Test case, Code example, Version/environment.
- **Feature — Heck & Zaidman (2017), Fig. 2, QC1 (completude):** QC1.1 Summary & description, Product version; QC1.2 Rationale; QC1.3 Use case or scenario, Possible solution. Fora: Keywords/tags e Link to code (gerenciamento do tracker, não texto do autor), Relative importance, Screens (sem interface gráfica no texto).
- **Mesmas restrições do Gerador do Grupo A (ADR 0005):** Opus 5.5, só o texto da issue, sem repositório, sem patch oficial, sem testes, ambiente limpo. Informação ausente na issue é marcada como "Not provided in the original issue", nunca inventada.
- Resolvedor, oráculo e medidas iguais aos de A e B.

## Alternativas
- Spec-Driven + critérios como entrada extra: mistura dois moldes; o efeito dos critérios não fica isolado.
- Deixar para os resultados finais.

## Consequências
- Compara "skill genérica" (A) com "critério da literatura" (C) e com o original (B), por tipo.
- +1 execução do Resolvedor por issue bug/feature.
- O ADR 0004 dizia "três braços: rejeitado para amanhã". Revertido em 2026-10-26 por decisão do Caio, com apresentação à tarde.

## Resultado (2026-10-26, 01:35–05:01)
269/269 issues bug/feature. RQ1 nas mesmas 269: A 191, B 189, C 188 (bug: 166/162/161; feature: 25/27/27). Vazamento do Gerador (cita arquivo do fix oficial ausente na issue): A 46, C 5. C custa quase igual a B em tokens; A custa ~40% a mais na entrada.
