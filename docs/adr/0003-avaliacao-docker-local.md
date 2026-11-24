# 0003 — Avaliação SWE-bench em Docker local

Data: 2026-10-25 · Status: aceita

## Contexto
Oráculo = testes FAIL_TO_PASS/PASS_TO_PASS do SWE-bench, rodados em container. Máquina medida em 2026-10-25: Docker 29, 30 GB RAM, 14 CPUs, **24 GB de disco livre** (37 GB recuperáveis em imagens Docker de outros projetos).

## Decisão
Avaliação local com o harness oficial `swebench`. O mesmo container de instância serve ao Resolvedor e ao avaliador.

## Validação do oráculo (adicionada 2026-10-25)
Teste com o patch oficial em `psf__requests-2317`: 8/8 FAIL_TO_PASS passam, mas 2 PASS_TO_PASS de timeout de rede (`TestTimeout::test_connect_timeout`, `test_total_timeout_connect`) falham neste ambiente (Docker remoto no minikube). Logo, nem o fix oficial conta como resolvido.
Decisão: antes de rodar o Resolvedor, cada issue é avaliada com o patch oficial; issue que não resolve aqui é **excluída** e listada como tal. Repositórios com testes de rede (requests) devem perder mais issues.

## Patch vazio e falhas de infraestrutura (adicionado 2026-10-25)
- Patch vazio: o avaliador do SWE-bench pula sem gerar relatório. Conta como **não resolvida** (`patch_vazio` no relatório). Primeiro caso: `sympy__sympy-11897`, grupo skill. O agente concluiu que o comportamento já estava certo.
- Falha do Resolvedor (cota, login) ou do avaliador (sem relatório): **não** conta como não resolvida. A execução é refeita após 15 min, até 8 tentativas.
- Execução em 2 processos paralelos, com posições alternadas da mesma lista ordenada. A amostra não muda.

## Download de imagens (adicionado 2026-10-26)
Com 3 processos, três imagens de matplotlib (7 GB cada) foram baixadas ao mesmo tempo e o disco caiu a 4 GB. Correção: um download por vez, sob trava em arquivo (`runs/.download.lock`), só com 12 GB livres. Restrição de ambiente que volta nos resultados finais.

## Alternativas
- Nuvem (sb-cli / Modal): sem limite de disco, mas mais uma conta e dependência externa às vésperas da apresentação.

## Consequências
- Disco limita N do piloto: cada instância tem imagem própria (camadas de ambiente compartilhadas por repo/versão). Preferir poucos repositórios.
- Limpar imagens após avaliar cada lote.

## Deferred
- Liberar os 37 GB de imagens antigas: decisão do Caio.
