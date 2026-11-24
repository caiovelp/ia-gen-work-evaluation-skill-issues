# 0002 — Resolvedor: Claude Code headless com Sonnet 5.5, dentro do container do SWE-bench

Data: 2026-10-25 · Status: aceita (revisada duas vezes no mesmo dia)

## Contexto
A proposta (slide 9) usa Google Antigravity com Gemini. O experimento precisa de 2×N execuções sem intervenção humana, cada uma partindo do commit pré-fix, com tokens e tempo medidos e o patch final extraído para o avaliador do SWE-bench. Antigravity é IDE: não foi verificado que roda por script nem que reporta tokens.

Histórico da decisão em 2026-10-25:
1. mini-SWE-agent + Gemini. Caído: Caio só tem free tier do Gemini; cada execução faz dezenas de chamadas.
2. mini-SWE-agent + Claude. Caído: Caio tem assinatura do Claude, não chave de API; mini-SWE-agent exige chave.

Justificativa usada na apresentação (do Caio, 2026-10-26): Antigravity com Gemini não foi usado porque a cota gratuita do Gemini não cobre o experimento (~860 execuções do agente), e o Caio tem assinatura do Claude.

## Decisão
- **Agente:** Claude Code CLI em modo não interativo (`claude -p`), modelo `claude-sonnet-5-5`, autenticado pela assinatura do Caio via token de longa duração (`claude setup-token` → `CLAUDE_CODE_OAUTH_TOKEN`). O token nunca é gravado no projeto.
- **Onde roda:** dentro do container oficial da instância SWE-bench, no repositório no commit pré-fix. Container novo por execução (contexto zerado, sem CLAUDE.md, skills ou memória do host).
- **Entrada:** o texto da issue do grupo (A ou B) e uma instrução fixa e igual para os dois grupos.
- **Ferramentas:** sem WebFetch e WebSearch (impede buscar o fix na internet). Permissões liberadas dentro do container (autonomia estrita).
- **Teto:** sem limite de passos nem de custo (escolha do Caio). Limite de **60 min de relógio** por execução, só contra processo travado (aceito pelo Caio em 2026-10-25); quem estourar conta como "não resolvida por tempo" e é reportada à parte.
- **Medidas:** `--output-format json` dá tokens (entrada, saída, cache), custo estimado, turnos e duração. Patch = `git diff` do container ao fim.

## Alternativas
- Antigravity manual: fiel à proposta, trabalho manual por issue, RQ2 em risco.
- mini-SWE-agent (Gemini ou Claude): exige chave de API.

## Consequências
- Slide de método diz as trocas: ferramenta (automação + medição de tokens) e modelo (cota/acesso).
- Gerador (Opus 5.5, ADR 0005) e Resolvedor (Sonnet 5.5) são da mesma família. Declarar.
- Custo em US$ do JSON é estimativa de preço de API; na assinatura o gasto real é cota. Reportar tokens como medida principal.
- Sem teto, uma execução pode demorar muito e reduzir N do piloto.

## Deferred
- **Assumido, não verificado:** Profa. Vania aceita trocar Antigravity/Gemini por Claude Code/Claude.
- **Assumido, não verificado:** a cota da assinatura aguenta o piloto até 00:00.
- ~~Histórico git futuro~~ **Verificado em 2026-10-25** em `psf__requests-2317`: `git log --all` = `git log` = 3.690 commits, um único branch `main`, sem remote. Sem commits futuros na imagem.
- **Ameaça declarada, não tratada:** o Resolvedor ainda tem rede via Bash (a API do Claude precisa dela), então poderia baixar o fix por `curl`/`pip`.
  **Verificado em 2026-10-25 (592 execuções):** `web_search_requests` = `web_fetch_requests` = 0 em todas. No texto final do agente, as únicas menções de rede são `pip install mpmath`/`asgiref` (17 casos) para conseguir rodar o código. Nenhum `curl`, `wget`, `git clone` ou github. Limite: só o texto final foi salvo, não a transcrição completa de comandos (`--output-format stream-json` resolveria nos resultados finais). O avaliador usa container novo + patch, então pacotes instalados pelo agente não entram na avaliação.

## Custo estimado (2026-10-26)
O `total_cost_usd` da saída do Claude Code usa US$ 0,10/milhão na leitura de cache do Sonnet 5.5; a tabela oficial da Anthropic (referência da skill `claude-api`, cache de 2026-10-06) diz US$ 0,20. Entrada (2,00), saída (10,00) e escrita de cache de 1 h (4,00 = 2× entrada) batem. O slide da RQ2 recalcula o custo a partir dos tokens com os preços oficiais; todas as escritas de cache foram de 1 h. Mediana nas 269 bug/feature: A 0,067, B 0,049, C 0,052.

## Reexecução para ilustrar (2026-10-26)
Como os passos das 861 execuções não foram salvos, `python piloto.py ilustrar <issue> original` reexecuta uma issue com `--output-format stream-json` e guarda cada ação em `runs/ilustracao/`. Fora das tabelas.
- `psf__requests-2148`: descartada como exemplo de memória. O stack trace da issue cita `requests/models.py`, `iter_content` e `urllib3/response.py`; o agente seguiu a pista. A reexecução também saiu diferente da execução original (8 passos e patch em 2 arquivos, contra 4 e 1), um exemplo concreto de não determinismo.
- `pytest-dev__pytest-5221` (slide): a issue não cita arquivo nem função; no 1º passo o agente busca `_showfixtures_main` em `src/_pytest/python.py`, escreve "Upstream format: name [scope] -- path", edita, encerra sem rodar testes; 9 s; passa nos testes do SWE-bench.
- Medida mais rigorosa para o cartão de memória: resolvida em até 5 passos **e** a issue não cita (caixa-insensível) o arquivo corrigido. Nas 269 bug/feature: 146 resolvidas em até 5 passos, 74 sem pista no texto.
