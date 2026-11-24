# 0010 — Corpus dos resultados finais: issues resolvidas do SAPOS

Data: 2026-10-27 · Status: proposta (sugestão da Profa. Vania, a decidir nos resultados finais)

## Contexto
Os resultados parciais mostraram que o SWE-bench Lite está contaminado (ADR 0002, ADR 0005, slides 9–10): a reescrita cita arquivos do fix oficial que a issue não cita (A 46 e C 5 de 269), e o resolvedor acerta em até 5 passos issues que nem citam o arquivo corrigido (74 de 269). A Profa. Vania sugeriu usar issues já resolvidas do **SAPOS**, projeto open source da UFF em que o Caio fez o TCC.

Fatos verificados em 2026-10-27 (API do GitHub):
- Repositório `gems-uff/sapos`: gestão de programas de pós-graduação (matrículas, disciplinas, orientação, bolsas, requisitos).
- Linguagem principal: **Ruby** (Rails). Criado em 2012-03-14; último push em 2026-10-27.
- 432 issues fechadas; 42 fechadas criadas a partir de 2025-06-01; 81 abertas; 33 estrelas.

## Decisão (proposta)
Trocar o SWE-bench Lite por issues fechadas do SAPOS nos resultados finais, mantendo os grupos A, B e C e as RQs.

## Por que ajuda
- Projeto pequeno e pouco popular: menos chance de as issues e os fixes estarem memorizados do que no django ou no sympy.
- Issues recentes (depois do corte de treino dos modelos) reduzem ainda mais a contaminação.
- O Caio conhece o código (TCC): pode julgar se a issue e o fix servem e montar o oráculo.

## Alternativas
- SWE-rebench ou SWE-bench-Live (issues posteriores ao corte de treino, já com ambiente e testes prontos).
- Combinar: SAPOS como estudo de caso e SWE-rebench como comparação.

## Deferred (a resolver antes de rodar)
- **Oráculo:** o SWE-bench traz testes fail-to-pass por issue; no SAPOS é preciso montá-los. Quantas issues fechadas têm PR com teste automatizado (RSpec)? Sem teste, não há "resolvida" automática.
- **Ambiente:** imagem Docker do SAPOS (Ruby, Rails, banco), uma por versão do código, no commit anterior ao fix.
- **Harness:** o avaliador do SWE-bench é feito para Python; para Ruby precisa de avaliador próprio, ou do suporte multilíngue de alguma versão do SWE-bench (verificar).
- **RQ3:** o ruff é só para Python; para Ruby, um linter como o RuboCop.
- **Contaminação continua possível:** o SAPOS é público no GitHub desde 2012. Preferir issues criadas depois do corte de treino do Sonnet 5.5 e do Opus 5.5, e repetir a medida de vazamento (ADR 0005).
- **Idioma:** verificar se as issues estão em português; a reescrita e os critérios (Bettenburg, Heck) foram aplicados até aqui em inglês.
- **Classificação bug/feature:** a skill (ADR 0008) nunca foi validada em issues do SAPOS.
- **Tamanho:** 42 issues fechadas recentes podem ser poucas depois dos filtros (com teste, bug/feature). Repetições por issue (ADR 0004) ajudam a compensar.

## Levantamento das candidatas (2026-10-27, `sapos_candidatas.py` → `runs/sapos/candidatas.csv`)
- Ligação issue → correção: só 16 das 432 issues fechadas têm PR ou commit ligado formalmente no GitHub. No SAPOS os commits citam a issue no assunto ("Issue #560: ..."); por essa via, **360** ficam ligadas a pelo menos um commit do ramo principal. 71 não têm ligação nenhuma.
- Critérios 1 e 2 do SWE-bench (correção mexe em teste **e** em código): **117 issues**. Criadas a partir de 2025-06: 29 (27 em 2026).
- Tipo: as labels do SAPOS são números de versão (milestones), mais `duplicate`, `invalid`, `wontfix`, `Migration`, `dependencies`, `wiki`, `TCC`. **Nenhuma candidata tem label de tipo bug/feature.** A classificação teria que vir da skill (ADR 0008).
- Cuidados vistos na lista: parte das 117 não é bug nem feature (ex.: #642 atualizar Rails, #644 zerar ofensas do rubocop, #682 separar checagens do CI); a correção às vezes se espalha por vários commits (até 13), diferente do PR único do SWE-bench; "mexe em teste" inclui factories e specs de feature, que não garantem um teste fail-to-pass.
- Falta o critério 3: montar o ambiente no commit anterior (`commit_base`), aplicar só os testes da correção, ver quais falham, aplicar o código e ver quais passam.
