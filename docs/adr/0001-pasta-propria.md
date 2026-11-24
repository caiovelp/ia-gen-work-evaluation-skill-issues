# 0001 — Projeto em pasta própria, separado do mestrado

Data: 2026-10-25 · Status: aceita

## Contexto
Disciplina "IA generativa para Engenharia de Software", 3 apresentações (ideia, resultados parciais, resultados finais). A ideia está em `docs/Agent_Skills_Issue_Resolution_Proposta.pdf`. O estudo é **outro** que o do mestrado (`~/mestrado/agentic-issue-analysis`, caracterização de issues abertas por agentes). Parecido só em um ponto: estrutura/completude de issue.

## Decisão
Projeto em `~/disciplinas/ia-gen-es`, git próprio. Coisas do mestrado (instrumento de completude, skill de classificação de tipo) entram **copiadas**, nunca importadas do repo do mestrado.

## Alternativas
- `~/mestrado/agent-skills-issue-resolution`: rejeitada pelo Caio.
- Subpasta do repo do mestrado: mistura dois estudos e a memória do Claude do mestrado.

## Consequências
- Commits só com autorização do Caio (mesma regra do mestrado).
