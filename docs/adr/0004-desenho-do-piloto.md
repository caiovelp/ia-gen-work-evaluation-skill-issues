# 0004 — Desenho do piloto para a apresentação 2

Data: 2026-10-25 · Status: aceita

## Contexto
Apresentação 2 (resultados parciais) é em 2026-10-26. Decisões tomadas em 2026-10-25 às ~11h40, com ~12h de trabalho até 00:00. Chave Gemini só free tier. Disco livre ~24 GB (ADR 0003).

## Decisão
- **Grupo A (skill):** issue reescrita com a skill Spec-Driven Development do Osmani (`~/.agents/skills/spec-driven-development/SKILL.md`, instalada em 2026-08-17).
- **Grupo B (baseline):** `problem_statement` original do SWE-bench Lite, sem reescrita.
- **Tamanho:** quantas issues couberem até 00:00 de 2026-10-26 (meia-noite de hoje), 1 execução por issue por grupo, mesmas issues nos dois grupos (pareado). Ordem fixa sorteada com semente, repositórios de imagem leve primeiro. Os dois grupos da issue *i* rodam antes de começar a *i+1*, alternando qual grupo vai primeiro, para o corte das 00:00 não deixar grupos com N diferente.
- **O que é "resultado parcial":** pipeline rodando ponta a ponta + tabela descritiva (resolvidas por grupo, tokens, tempo, linhas do patch). Sem teste estatístico.

## Alternativas
- Skill de bug report baseada no instrumento do mestrado (Zimmermann/Bettenburg): rejeitada para amanhã; desvio da proposta.
- Três braços (original, Spec-Driven, bug report): custo e disco ×1,5.
- Baseline = reescrita por LLM sem skill: isolaria a skill do "efeito de reescrever", custa uma geração a mais por issue.

## Consequências
- Comparação A x B mistura dois efeitos: o da skill e o de um LLM reescrever o texto. Declarar como limitação.
- Spec-Driven é molde de especificação de feature; SWE-bench Lite é quase todo bug. Declarar como ameaça.
- Com N pequeno e 1 execução, nenhuma diferença é conclusiva. Apresentar como piloto.

## Deferred
- Repetições por issue (agente é estocástico) e N final: resultados finais.
- Teste pareado (McNemar para resolvida/não; Wilcoxon para tokens e tempo): resultados finais.
- Terceiro braço com skill de bug report do mestrado: candidato para resultados finais.

## Resultado da execução (2026-10-25, 12:00–21:40)
Coube o SWE-bench Lite inteiro: 300 issues tentadas, 4 excluídas pelo oráculo (requests, testes de rede), 296 pareadas, 592 execuções do Resolvedor. Até 3 processos paralelos (ADR 0003). Repetições e testes estatísticos continuam para os resultados finais.

## McNemar como ilustração (2026-10-26)
A pedido do Caio (entender o teste), McNemar exato nas 269 issues bug/feature entra no slide de próximos passos como exemplo: A×B 22 × 20 (p = 0,88), C×B 13 × 14 (p = 1,00). Não é a análise final: falta repetição por issue.
