# 0008 — Classificação bug/feature das issues do SWE-bench Lite

Data: 2026-10-26 · Status: aceita

## Contexto
O Caio quer os resultados separados por tipo (só bug e feature), porque os critérios de qualidade da literatura são diferentes para cada um (Bettenburg et al. 2008 para bug; Heck & Zaidman 2017 para feature request). O SWE-bench Lite não traz tipo. A proposta (slide 7) dizia "categoria única — só bugs ou só features", mas não havia classificação feita.

## Decisão
- Skill de classificação do mestrado (`~/mestrado/agentic-issue-analysis/.claude/skills/issue-type-classification`), prompt de tipo copiado para `prompts/classificacao_tipo_herzig.md`: regras da Tabela III de Herzig, Just & Zeller (2013) no molde de Colavito et al. (2024), **zero-shot**, Opus 5.5, uma chamada por issue, ambiente limpo (sem ferramentas, configuração vazia).
- Entrada: `problem_statement` do SWE-bench. Título = primeira linha; corpo = o resto (o dataset não separa título e corpo).
- Só **bug** e **feature** entram na análise por categoria. `neither` e `discard` ficam fora dela (continuam no resultado geral A × B).

## Alternativas
- Skill + amostra anotada pelo Caio para ter κ neste dataset: mais forte, custa tempo que não há antes da apresentação de 2026-10-26.

## Consequências
- Validação da skill no mestrado: κ 0,714 contra a anotação do Caio, em issues abertas por agentes. **Nunca validada em issues Python do SWE-bench.** As regras de Herzig foram escritas para projetos Java (ex.: "NullPointerException").
- Uma chamada por issue, não 10 rodadas com voto da maioria como no mestrado. Instabilidade de rótulo não medida.

## Deferred
- κ neste dataset (amostra anotada pelo Caio): resultados finais.
