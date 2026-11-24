# 0006 — Medidas de qualidade do patch (RQ3) no piloto

Data: 2026-10-25 · Status: aceita

## Contexto
Slide 11 da proposta deixou "métricas de linter e complexidade" em aberto.

## Decisão
Para cada patch gerado:
- linhas adicionadas, linhas removidas e arquivos tocados, ao lado dos mesmos números do patch oficial;
- avisos novos do `ruff` (regras padrão) nas linhas alteradas: avisos depois do patch menos avisos antes, só nos arquivos tocados.

## Alternativas
- Só linhas do patch.
- Linhas + ruff + complexidade ciclomática (radon).

## Deferred
- Complexidade ciclomática: resultados finais, se fizer sentido.

## Revisão (2026-10-26)
O Caio achou "avisos novos do ruff" pouco informativo. Entram no slide: **patch mexe nos mesmos arquivos do fix oficial** (maior é melhor) e **patch quebra teste que passava antes** (PASS_TO_PASS com falha; menor é melhor), além de linhas e arquivos tocados. O ruff sai do slide e fica só nas notas (A 21, B 11, C 10 avisos novos em 269 patches).
