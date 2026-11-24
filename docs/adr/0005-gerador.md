# 0005 — Gerador: Claude Opus 5.5 aplica só a fase Specify, vendo só o texto da issue

Data: 2026-10-25 · Status: aceita

## Contexto
O Gerador reescreve a issue original para o Grupo A com a skill Spec-Driven Development (ADR 0004). A skill é interativa: pede humano aprovando cada fase (Specify, Plan, Tasks, Implement). No experimento não há humano. O Gerador também pode lembrar o fix oficial do SWE-bench e escrevê-lo só na versão A (vazamento a favor do tratamento).

## Decisão
- **Modelo:** Claude Opus 5.5 rodando no Claude Code, com a skill carregada como texto de instrução.
- **Aplicação:** só a fase Specify, em um tiro. Saída = a spec (Objetivo, Critérios de sucesso, Suposições, Perguntas abertas e demais seções do molde). Sem Plan, Tasks nem Implement: isso é trabalho do Resolvedor. Perguntas que a skill faria ao humano ficam em "Perguntas abertas"; suposições ficam listadas.
- **Ambiente limpo:** `claude -p` com diretório de configuração vazio (`CLAUDE_CONFIG_DIR`) e pasta de trabalho vazia, autenticado pelo token da assinatura. Sem isso, os hooks e plugins do Claude Code do Caio (ex.: estilo de escrita resumido) entrariam só no texto do Grupo A. `--bare` não serve: não aceita login por assinatura. Conferir a primeira spec gerada procurando marcas desses hooks.
- **Entrada:** só `problem_statement` original. Gerador não vê repositório, patch oficial nem testes.
- **Medida de vazamento:** para cada issue, arquivos e funções/classes tocados pelo patch oficial que aparecem na versão A e **não** aparecem na original. Reportado como 1 número no slide. Nomes só com letras minúsculas e menos de 6 caracteres (`open`, `match`) não contam: são palavras comuns, falso positivo visto em 2026-10-25. Métodos especiais (`__init__`, `__mul__`) também não contam. O slide separa specs que citam **arquivo** do patch oficial (sinal mais forte) das que citam **função/classe**.

## Alternativas
- Gemini Pro via API: mesma família da proposta, cota free tier insuficiente.
- Specify sem seções de repositório (Commands, Project Structure, Code Style).
- Specify + Plan: mais chance de o Gerador resolver a issue no texto.

## Consequências
- Seções do molde que dependem do repositório podem sair inventadas ou vazias. Fica visível na medida de vazamento e na leitura de exemplos.
- Gerador e Resolvedor (Sonnet 5.5, ADR 0002) são da mesma família.
