# 0011 — Resultados finais: SAPOS, issues de 2024 em diante

Data: 2026-11-23 · Status: aceita · Prazo: apresentação pronta em 2026-11-24 (terça) à noite; apresentação 2026-11-25

## Contexto
ADR 0010 propôs o SAPOS (`gems-uff/sapos`) contra a contaminação do SWE-bench. Levantamento em 2026-11-23:
- Testes rodam em SQLite (`config/database.yml`); CI usa MariaDB e Selenium (Chrome/Firefox) para specs de tela.
- Ruby 3.2.5 até 2026-07; 3.3/3.4 depois (troca de Rails 7.0 → 7.1 → 8.x em 2026). Antes de 2024, Rails/Ruby antigos: fora de alcance até terça.
- Em 2026, centenas de commits têm o Claude como coautor (Opus 5: 112 + 66; Opus 5.5: 92; "Claude": 82). As issues de 2026 são quase todas do Leo Murta (24 de 29 candidatas), longas (2–5 mil caracteres), em português. O repositório tem `CLAUDE.md` → `AGENTS.md` (377 linhas de instruções para agentes).

## Decisão
- **Recorte:** candidatas criadas de 2024 em diante (~33 antes da validação dos testes). Duas imagens Docker (Ruby 3.2.5 e Ruby da época posterior).
- **Validação no molde do SWE-bench:** no commit anterior à correção, aplicar só as mudanças em `spec/`, rodar os specs tocados; aplicar o código; rodar de novo. FAIL_TO_PASS = falhava e passa; PASS_TO_PASS = passava e continua. Fica só issue com ≥ 1 FAIL_TO_PASS.
- **Agente que resolve:** sem `CLAUDE.md`, `AGENTS.md` e instruções de agente do repositório no container (igual ao SWE-bench dos parciais: só a issue e o código). Sem commits posteriores à base no histórico.
- **Grupos:** A (Spec-Driven), B (original), C (literatura por tipo), como nos parciais. Reescrita em **português**, o idioma da issue.
- **Classificação:** skill do mestrado (ADR 0008). O Caio anota às cegas (`runs/sapos/anotacao_tipo_cega.xlsx`, sem a saída do Claude; aba com as mesmas regras de Herzig) para medir κ no SAPOS. O experimento usa o tipo da skill.
- **Entregáveis:** slides (estilo das apresentações 1 e 2) + paper de 4 páginas + 1 de referências no template SBC (CBSoft/SBES), com seções de disponibilidade de artefatos e de uso de IA generativa; `.tex` gerado aqui e colado pelo Caio no Overleaf.

## Alternativas
- Só 2026 (pós-corte, homogêneo, menos issues); só antes de 2026 (~6, poucas demais).
- Manter `AGENTS.md` (mais realista, mas mistura instruções do projeto com o efeito da issue).
- Reescrever em inglês (mistura tradução com reescrita).

## Consequências e ameaças
- Correções de 2026 coescritas pelo Claude: o resolvedor (Sonnet 5.5) é da mesma família que escreveu o fix. Não é memorização, mas é proximidade de estilo. Comparar 2024–2025 × 2026.
- Issues de 2026 longas e detalhadas (possivelmente escritas com IA) já são "estruturadas": o efeito da reescrita tende a ser menor.
- N pequeno (dezenas): resultados descritivos; repetições continuam pendentes (ADR 0004).

## Paper (decidido em 2026-11-23)
- Template oficial do CBSoft 2026: `acmart` com `sigconf` (adaptação ACM, não o estilo SBC antigo), zip em cbsoft.sbc.org.br/2026/Template_para_eventos_do_CBSoft.zip. Limite da disciplina: 4 páginas de conteúdo + 1 de referências. Português.
- Seção não numerada "Disponibilidade de Artefatos" depois da Conclusão. Uso de IA generativa declarado nos agradecimentos (política do SBES: proíbe seções "integralmente produzidas" por IA; exige dizer o que foi gerado e com qual ferramenta).
- Divisão: Claude entrega esqueleto compilando (seções, tabelas, figura, referências, tópicos com números); **o Caio escreve a prosa**. Agradecimentos declaram código, execução do experimento, tabelas e figura feitos com Claude Opus 5.5.

## Execução e resultado (2026-11-23, 09:40–13:15)
- Validação: 36 candidatas → **27 tarefas** (5 sem teste que falha antes da correção, 4 sem arquivo `_spec.rb`). 3 montadas por **diff acumulado** (plano B quando o cherry-pick dos commits da issue conflita; pode trazer mudanças de outras issues nos mesmos arquivos). Tipos pela skill: 15 bug, 3 feature, 8 neither, 1 discard → 18 com os três grupos.
- Ajustes de ambiente descobertos no caminho: configs `.example` copiadas como no CI; `bundle install` + `db:schema:load` antes de cada rodada de testes (correções com gem nova ou migração); Chromium local com `--no-sandbox` e `SE_OFFLINE` (bases antigas fixam Chrome e o Selenium Manager não baixa pela rede do minikube); imagem Ruby 3.2.11 para a #640 (`Gemfile` trava `~> 3.2.11`); leitura de patches em bytes (CRLF).
- Defeitos do avaliador corrigidos depois da execução: (a) `Gemfile.lock` regenerado pelo ambiente entrava no patch do agente → excluído na aplicação; #503 reavaliada nos três grupos com os patches existentes; (b) CRLF perdido ao extrair o patch do agente → #530 (B) e #655 (C) **reexecutadas** (o patch original não era recuperável). Avaliador conferido com o fix oficial (#623 e #657 resolvidas).
- **Resultado:** nas 18 bug/feature, A 4, B 4, C 4 (22%); nas 27, A 4 e B 4 (15%). Mesmas 3 issues resolvidas pelos três grupos; A troca 1 (#624 por #680). Patch vazio: A 7/27, B 4/27, C 0/18. Vazamento da reescrita (cita arquivo do fix ausente na issue): A 1/27, C 0/18 (SWE-bench: 46 e 5 de 269). Tokens de entrada parecidos (mediana 90, 92, 96 mil); custo estimado A 0,088 contra 0,063 (B) e 0,058 (C).
- Nenhuma execução usou WebSearch/WebFetch; nenhuma estourou 60 min.
- As 6 primeiras tarefas (#621, #623, #625, #631, #636, #657) foram validadas e avaliadas na imagem com Firefox; as outras 21, na imagem com Chromium. Dentro de cada tarefa, os três grupos usaram a mesma imagem.
- Empate 4/4/4 conferido (2026-11-23): textos e sessões distintos por grupo; 3 issues fáceis comuns (#635, #648, #664; na #648 o patch é idêntico nos três) e uma troca (#624 só A; #680 B e C, A com patch vazio). Issues do SAPOS mais longas (mediana 1.828 × 1.070 caracteres) e citam mais o arquivo corrigido (56% × 46%).

## Ampliação do recorte (2026-11-23, decisão do Caio)
O corte por **data de criação** (2024 em diante) estava no lugar errado: o que limita é o ambiente do **commit base**. Das 81 candidatas anteriores a 2024, 12 foram corrigidas recentemente e a base já usa Ruby 3.2/3.4 (#150, #183, #184, #210, #224, #286, #399, #401, #405, #408, #448, #449). Entram na validação com as mesmas imagens. As outras 69 exigem Rails 3–6 e continuam fora.
Consequência: o texto dessas issues é antigo (pode estar no treino dos modelos), mas a correção é recente; dá para comparar com as de 2024 em diante.

## Critério de validação, como no SWE-bench (Jimenez et al., 2024)
(1) issue ligada à correção (aqui: commits que citam #N); (2) correção traz teste (`spec/`); (3) execução: no commit base, só o patch de teste → roda; + código → roda; ≥ 1 FAIL_TO_PASS. Não aplicados os filtros extras do SWE-bench Lite (issue curta, correção em um arquivo).
