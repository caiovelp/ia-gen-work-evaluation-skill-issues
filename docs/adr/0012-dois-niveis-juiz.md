# 0012 — Dois níveis de avaliação no SAPOS: testes (estrito) e juiz LLM calibrado (amplo)

Data: 2026-11-23 · Status: aceita

## Contexto
O critério do SWE-bench (ADR 0011) deixou ~30 tarefas. O Caio achou rígido para issues reais de um único projeto. Levantamento: 432 issues fechadas, 359 ligadas a commits, 340 com mudança de código, **72 com commit base em Ruby 3.2/3.4** (ambiente que já roda), 48 delas com teste. As outras ~270 exigem Rails 3–6: limite de ambiente, não de critério. Sem teste que falhe antes da correção não há oráculo automático; afrouxar exige outro oráculo.

## Decisão
- **Nível 1 (estrito):** tarefas com ≥ 1 FAIL_TO_PASS, avaliadas pelos testes (como antes). Resultado principal.
- **Nível 2 (amplo):** as 72 issues com correção em código e base em Ruby 3.2/3.4. O agente roda igual (grupos A, B, C; C só bug/feature). "Resolvida" decidida por um **juiz LLM** (Opus 5.5): recebe o texto original da issue, a correção oficial (só código) e o patch do agente; responde resolve / parcial / não resolve. O juiz não sabe de que grupo veio o patch.
- **Calibração:** o juiz também julga todas as execuções do nível 1; concordância juiz × testes (acurácia, κ, precisão/recall de "resolve") é reportada. Nível 2 só é apresentado junto com essa concordância.

## Alternativas
- Só localização (mesmos arquivos do fix): objetiva, mas mede onde mexeu, não se acertou.
- Ambientes Rails 5–6 (Ruby 2.x): mantém testes, +~25 issues, arriscado até terça.
- Manter o estrito.

## Consequências e ameaças
- Juiz da mesma família do Gerador e do Resolvedor (Claude). Mitigação parcial: calibração contra testes e cegueira quanto ao grupo.
- Correção oficial pode estar incompleta ou ter mudanças de outras issues (diff acumulado); o juiz é instruído a julgar se a issue foi resolvida, usando a correção como referência, não como gabarito literal.

## Calibração v1 (2026-11-23)
Juiz v1 nas 72 execuções do nível 1: testes resolvida 12 → juiz resolve 11, parcial 1; testes não resolvida 60 → juiz resolve 19, parcial 26, não resolve 15. "Resolve" binário: precisão 37%, revocação 92%, acurácia 72%, κ ≈ 0,38. Generoso: superestimaria a taxa ~2,5×.

## Juiz v2 (decisão do Caio, 2026-11-23)
Uma única reescrita da régua, mais rígida ("resolve" só se cobrir cada mudança de comportamento da correção oficial que a issue exige; na dúvida, "parcial"). Para não ajustar e medir no mesmo dado: tarefas do nível 1 divididas por issue em metade de desenvolvimento e metade de teste (hash do número da issue); κ reportado na metade de teste. Sem segunda iteração.
- **Resultado v2:** todas (78 execuções do nível 1) κ 0,76, precisão 0,77, revocação 0,83; metade de teste (25) κ 0,90, precisão 0,86, revocação 1,00. Nível 2 usa o juiz v2.
