# Resultados parciais — notas para a fala

Executado em 2026-10-25 (A e B) e 2026-10-26 (classificação e C). Números de `runs/tabela.csv` (`python piloto.py medir`). Slides em `docs/apresentacao2/`. Decisões em `docs/adr/`.

## Slide a slide

**1 · O que mudou e por quê**
- Agente resolvedor: Antigravity com Gemini não foi usado porque a cota gratuita do Gemini não cobre ~860 execuções; há assinatura do Claude. Agora: Sonnet 5.5.
- Agente da reescrita: o Opus 5.5 é o "LLM de alto desempenho". O que mudou: ele aplica só a 1ª das 4 etapas da skill (escrever a especificação; as outras são planejar, quebrar em tarefas e implementar), porque a skill para em cada etapa esperando aprovação humana. Ele também vê só o texto da issue, sem o repositório, para não copiar o fix.
- Grupos: A (skill) e B (original) como na proposta, mais C (critérios da literatura), porque a skill não segue critérios de qualidade de bug nem de feature.
- Oráculo mantido. 4 issues saíram: nem o fix oficial passa neste ambiente (testes de rede do requests).

**2 · Metodologia:** amostrar (300) → classificar (bug ou feature) → gerar (A, B, C) → agente resolve (Sonnet 5.5, no container da issue) → testes do SWE-bench → resultados (RQ1, RQ2, RQ3).

**3 · Classificação**
- O SWE-bench Lite não traz o tipo. Usamos a skill do mestrado (Herzig et al. 2013, Opus 5.5, zero-shot): 229 bug, 40 feature, 27 nenhum dos dois.
- Por que só bug e feature: são os tipos com critérios de qualidade de issue usados no mestrado (Bettenburg 2008 para bug, Heck & Zaidman 2017 para feature). Não afirmamos que outros tipos não tenham critério na literatura.
- 4 desconsideradas (das 300): nem o fix oficial passa nos testes neste ambiente, porque os testes do requests dependem de rede.
- Skill de classificação: criada no mestrado a partir de Herzig, Just & Zeller (ICSE 2013, Tabela III), com prompt no molde de Colavito et al. (MSR 2024).
- Concordância no mestrado (96 issues anotadas pelo Caio, 10 rodadas): κ 0,714; bug P 1,00 R 0,64; feature P 0,81 R 0,87.

**4 · Como cada grupo é:** A reescreve com o molde do Osmani; B é o original; C reescreve com os itens da literatura **no lugar** do molde do Osmani (não é Osmani + critérios).

**5 · A mesma issue em cada grupo (flask-4045):** B tem 230 caracteres; A vira 7.210 com 10 seções de especificação de projeto; C vira 1.132 com as 8 seções de Bettenburg, 4 marcadas "Not provided" (stack trace, caso de teste, código, versão).

**6 · RQ1 (mesmas 269 issues):** bug A 166 (72%), B 162 (71%), C 161 (70%); feature A 25 (62%), B 27 (68%), C 27 (68%). Diferenças de 1 a 4 issues.

**7 · RQ2 (mediana):** A custa mais (entrada 104 mil × 74 mil em B × 78 mil em C; saída 1.246 × 882 × 859; custo US$ 0,067 × 0,049 × 0,052; tempo 17 s × 14 s × 14 s). C custa quase o mesmo que B.
- Custo = tokens × preço oficial da API da Anthropic para o Sonnet 5.5 (US$/milhão: entrada 2,00, saída 10,00, escrita no cache de 1 h 4,00, leitura do cache 0,20). Recalculado por nós: o número pronto da ferramenta usava 0,10 na leitura de cache. Só o agente que resolve; a reescrita do Opus custaria a mais ~US$ 0,067 (A) e ~US$ 0,035 (C) por issue.

**8 · RQ3:**
- Mexe nos mesmos arquivos do fix oficial: A 227 (84%), B 249 (93%), C 251 (93%). Com a spec do Osmani, o agente vai mais para arquivos errados.
- Quebra teste que passava antes: A 13, B 11, C 7.
- Tamanho igual nos três (4 linhas, 1 arquivo) e perto do oficial (5 linhas).
- Fora do slide: avisos novos do ruff (linter de Python: variável indefinida, import não usado): A 21, B 11, C 10.

**9 · Ameaças**
- Vazamento (A 46, C 5 de 269): o Opus não vê o repositório, então nome de arquivo do fix só pode vir da memória. Issues e PRs do SWE-bench são públicos e estão no treino. O molde do Osmani pede "Estrutura do projeto" e "Comandos".
- Memória do resolvedor: 146 de 269 issues originais resolvidas em até 5 passos do agente; em 74 delas a issue nem cita o arquivo corrigido. Sem pista no texto e sem procurar, o agente vai direto ao lugar do fix.

**10 · O agente vai direto ao código (pytest-5221, reexecução registrada):** a issue (239 caracteres) não cita arquivo nem função. Passo 1: busca `_showfixtures_main` em `src/_pytest/python.py`. Passo 2: escreve "Upstream format: name [scope] -- path" (o formato da versão real do pytest). Passo 3: edita (+4 −2). Passo 4: encerra sem rodar testes. 9 s, passa nos testes do SWE-bench. Cuidado ao usar requests-2148 como exemplo: lá o stack trace da issue já aponta o arquivo.
- Classificação: as regras olham o texto, mas o κ 0,714 foi medido em issues escritas por agentes (mestrado); em issues humanas do SWE-bench nunca foi medido.

**10 · Próximos passos**
- Trocar o corpus: SWE-bench (2023) está contaminado. SWE-rebench (Nebius; issues por mês, cada modelo avaliado só em issues posteriores ao seu lançamento; roda 5 vezes por modelo) e SWE-bench-Live (Microsoft; issues de 2024 em diante, atualizável).
- Repetições: o agente não é determinístico; 3 a 5 tentativas por issue medem quanto o resultado varia sozinho.
- Estatística: McNemar olha só as discordâncias. A×B 22 × 20 (p = 0,88); C×B 13 × 14 (p = 1,00). Hoje, nenhuma diferença detectável. Wilcoxon faz o mesmo para tokens e tempo, comparando cada issue com ela mesma.

## Guardado fora dos slides: o que o Grupo C conseguiu tirar da issue original
Seção preenchida (escrita ou deduzida; julgamento do Opus): bug — passos, observado e esperado ~100%, código 85%, caso de teste 70%, stack trace 47%, versão 18%; feature — justificativa 98%, cenário 95%, solução 98%, versão 8%. Em ~28 dos 229 bugs o Opus disse explicitamente que o "esperado" foi deduzido.

## Checagens de integridade (861 execuções)
Falha de infraestrutura: 0. Patch que não aplicou: 1 (B) + 1 (C). Patch vazio: 1 (A). Estouro de 60 min: 0. WebSearch/WebFetch: 0. Rede via Bash: só `pip install` de dependência.

## Fontes dos benchmarks citados
- SWE-bench-Live: https://arxiv.org/abs/2505.23419
- SWE-rebench: https://arxiv.org/pdf/2505.20411

## Próximo corpus sugerido pela Profa. Vania (ADR 0010)
Issues já resolvidas do SAPOS (`gems-uff/sapos`, Ruby/Rails, projeto do TCC do Caio): 432 fechadas, 42 criadas a partir de 2025-06. Antes de rodar, resolver o oráculo (testes por issue), o ambiente Docker, o avaliador para Ruby e o idioma das issues.
