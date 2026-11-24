# Resultados finais — notas para a fala (7 minutos)

Slides: `docs/apresentacao3/Resultados_Finais.pdf`. Paper: `docs/paper/main.tex`. Decisões: `docs/adr/0011-resultados-finais-sapos.md` e `docs/adr/0012-dois-niveis-juiz.md`.

1. **Capa** (5 s).
2. **Pergunta e método** (~1 min): a mesma issue em três versões — A reescrita pelo Opus 5.5 com a skill Spec-Driven Development, B original, C reescrita com os itens de Bettenburg (bug) e Heck & Zaidman (feature). O Sonnet 5.5 resolve sozinho, no container do projeto.
3. **Parciais: SWE-bench Lite** (~1 min): 71/70/70% — sem diferença. Sinais de contaminação: a reescrita A cita o arquivo do fix em 46 issues; 74 resolvidas em até 5 passos sem a issue citar o arquivo. Por isso trocamos de corpus.
4. **SAPOS** (~1 min): sistema da UFF, Ruby on Rails, issues em português. 432 fechadas → 340 com correção em código → 67 com commit base num ambiente que conseguimos rodar (Ruby 3.2/3.4; o resto exige Rails 3–6) → 29 com teste que falha antes e passa depois (critério do SWE-bench). Dois níveis: **estrito** (29, avaliadas pelos testes) e **amplo** (67, avaliadas por um juiz LLM).
5. **RQ1** (~1 min): estrito 20% nos três grupos (20 bug/feature); amplo 15% em A e B (67), 14/12/9% em A/B/C nas 43 bug/feature. Contra ~70% no SWE-bench. O juiz foi calibrado nos testes do nível estrito: κ 0,76 (0,90 na metade não usada para ajustar a régua).
6. **RQ2 e RQ3** (~1 min): tokens parecidos; a skill custa mais (US$ 0,10 contra 0,08) e leva mais tempo; C acerta mais os arquivos (8 de 20). Fora da tabela: nas 29, a skill deixou o agente sem mudar nada em 7 issues (B: 4).
7. **Ameaças** (~40 s): correções de 2026 do SAPOS feitas com o Claude (mesma família do resolvedor); 1 execução por issue; amostra pequena e juiz LLM no nível amplo.
8. **Conclusão** (~30 s): reescrever não mudou a taxa; em issues novas a taxa cai de ~70% para ~20%; a skill genérica custou mais nos dois corpora.

## Perguntas prováveis

**Por que tão baixo no SAPOS?**
- O comportamento do agente é o mesmo nos dois corpora: poucos passos e quase nunca roda os testes (diz isso na resposta final em 72% das execuções no SWE-bench e 89% no SAPOS). No SWE-bench, 74% dessas execuções sem teste resolveram; no SAPOS, 19%. Sem um fix memorizado, a correção parcial não passa.
- As correções de 2026 do SAPOS foram feitas com o Claude **usando** o `AGENTS.md` do projeto; aqui o agente rodou sem ele (ADR 0011), para isolar o efeito do texto da issue.

**Por que A, B e C deram exatamente 4 no estrito?**
- Não são as mesmas 4. Três issues fáceis (#635, #648, #664: 1 teste, 1–2 arquivos) são resolvidas pelos três grupos; na #648 os três produziram o mesmo patch. Depois há uma troca: o A resolve a #624, e B e C não; B e C resolvem a #680, e o A não mudou nada.
- As issues do SAPOS já são detalhadas: mediana de 1.828 caracteres (SWE-bench: 1.070) e 56% citam o arquivo a corrigir (SWE-bench: 46%). Indício, não prova.

**Por que só 29 com testes, se 117 mexem em teste e código?**
- O limite é de ambiente: só 67 issues têm commit base em Ruby 3.2/3.4. Das que têm teste nesse ambiente, várias não têm teste que falhe antes da correção (o teste novo já passava) ou não trazem arquivo `_spec.rb`. Por isso o nível amplo, com juiz.

**Dá para confiar no juiz?**
- Calibrado contra os testes nas 78 execuções do nível estrito: primeira régua generosa (κ 0,38); uma única revisão mais rígida chegou a κ 0,76 (precisão 0,77, revocação 0,83) e 0,90 na metade não usada para ajustar. O juiz não sabe de que grupo veio o patch. Ameaça: é da mesma família (Claude) do Gerador e do Resolvedor.
