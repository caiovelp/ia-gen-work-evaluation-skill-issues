# Spec: Correções no Processo Seletivo (empate no ranking e validação de modelo de carta)

## Objetivo

Corrigir dois defeitos independentes no módulo de processo seletivo.

**Problema 1: empate na penúltima posição de um grupo do ranking**
Quando há empate na penúltima posição de algum grupo do ranking, a vaga não é descontada do total disponível para o grupo. Com isso, o número de vagas disponíveis fica maior do que o real.

**Problema 2: falta de validação do modelo de formulário de carta no edital**
Um edital pode exigir um número mínimo de cartas. Hoje o sistema não verifica se esse edital tem um modelo de formulário de carta configurado. A inconsistência só aparece quando o candidato submete a inscrição, e a submissão termina em erro.

**Usuários afetados:**
- Problema 1: gestores ou comissão do processo seletivo, que geram e consultam o ranking, e candidatos, cuja classificação depende das vagas.
- Problema 2: quem cadastra ou configura o edital e os candidatos que tentam se inscrever.

**Critérios de aceitação (rascunho, a confirmar):**
- AC1: Com empate na penúltima posição de um grupo, cada vaga atribuída é descontada do saldo de vagas do grupo, como acontece sem empate.
- AC2: O saldo de vagas de cada grupo após o ranqueamento é igual a "vagas do grupo − vagas efetivamente consumidas", com ou sem empate.
- AC3: Não é possível salvar ou publicar um edital com número mínimo de cartas maior que zero sem um modelo de formulário de carta. O sistema mostra uma mensagem de validação clara a quem configura o edital.
- AC4: A submissão de uma inscrição não termina em erro não tratado por falta de modelo de formulário de carta.
- AC5: Editais sem exigência de cartas (mínimo igual a zero ou não definido) continuam funcionando como hoje.

## Premissas

1. "Grupo do ranking" é uma divisão das vagas, por exemplo modalidade de concorrência, cota ou linha de pesquisa, e cada grupo tem seu próprio total de vagas.
2. "Penúltima posição" se refere à posição antes da última vaga disponível do grupo. O defeito talvez ocorra em outras posições, mas foi observado nessa.
3. O comportamento esperado com empate é que os empatados consumam vagas normalmente. A regra de desempate ou de ampliação de vagas em caso de empate não é informada (ver Perguntas em Aberto).
4. "Cartas" são cartas de recomendação ou referência enviadas por terceiros, preenchidas com um "modelo de formulário de carta" vinculado ao edital.
5. A correção do Problema 2 consiste em validar no cadastro ou edição do edital. Uma proteção adicional na submissão da inscrição seria desejável, mas isso precisa ser confirmado.
6. Os dois problemas são independentes e podem ser corrigidos, testados e entregues separadamente.
7. Pode haver editais já cadastrados no estado inválido do Problema 2: mínimo de cartas sem modelo.

## Stack Tecnológica

Não informado na issue original.

## Comandos

Não informado na issue original.
- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Não informado na issue original. A localização dos códigos de cálculo do ranking, cadastro do edital e submissão de inscrição é desconhecida.

## Estilo de Código

Não informado na issue original.

## Estratégia de Testes

O framework e a localização dos testes não foram informados na issue original. Cenários que os testes devem cobrir:

**Problema 1 (ranking):**
- Grupo sem empate: saldo de vagas correto (regressão).
- Empate na penúltima posição: saldo de vagas correto.
- Empate na última posição e em posições intermediárias, para verificar se o defeito se limita à penúltima.
- Vários grupos com empate em mais de um deles: a vaga é consumida do grupo correto e não vaza para outro.
- Grupo com apenas uma ou duas vagas, em que a "penúltima" coincide com a primeira.
- Vagas remanescentes que migram entre grupos, se essa regra existir.

**Problema 2 (edital e cartas):**
- Edital com mínimo de cartas maior que zero e sem modelo: a validação bloqueia e mostra a mensagem.
- Edital com mínimo de cartas maior que zero e com modelo: salva normalmente.
- Edital sem exigência de cartas e sem modelo: salva normalmente (regressão).
- Submissão de inscrição em edital válido com cartas: sucesso.
- Submissão de inscrição em edital legado inconsistente: comportamento definido sem erro não tratado (ver Perguntas em Aberto).

## Limites

- **Sempre:**
  - Escrever um teste que reproduza cada defeito antes de corrigi-lo.
  - Preservar o comportamento atual dos rankings sem empate e dos editais sem exigência de cartas.
  - Manter as correções dos dois problemas separadas, rastreáveis e testáveis de forma independente.
- **Perguntar antes:**
  - Mudar a regra de negócio de desempate ou de distribuição de vagas.
  - Recalcular ou alterar rankings já publicados.
  - Fazer migrações de dados ou mudanças de schema, por exemplo para tornar o modelo de carta obrigatório no banco.
  - Corrigir automaticamente editais existentes em estado inconsistente.
  - Adicionar dependências.
- **Nunca:**
  - Alterar resultados de processos seletivos já homologados sem aprovação.
  - Remover ou desabilitar testes existentes que falhem sem aprovação.
  - Silenciar o erro de submissão sem tratar a causa.

## Critérios de Sucesso

1. Um teste automatizado reproduz o Problema 1 (empate na penúltima posição) e passa após a correção, com o saldo de vagas do grupo correto.
2. Um teste automatizado reproduz o Problema 2. Após a correção, o edital inconsistente é rejeitado na configuração com uma mensagem clara.
3. Nenhuma inscrição em edital com exigência de cartas termina em erro não tratado por falta de modelo de formulário.
4. Os testes de regressão de ranking sem empate e de editais sem cartas continuam passando.
5. O tratamento de editais legados inconsistentes está definido e implementado conforme a resposta às Perguntas em Aberto.

## Perguntas em Aberto

**Problema 1:**
1. Qual é a regra esperada quando há empate? Todos os empatados são classificados, mesmo excedendo o número de vagas, ou existe um critério de desempate?
2. Quantas vagas deveriam ser consumidas no cenário relatado (um exemplo numérico de vagas, posições e notas)? Qual é o resultado atual e qual era o esperado?
3. O defeito ocorre só na penúltima posição ou também em outras posições com empate?
4. Vagas não preenchidas de um grupo migram para outros grupos? O defeito afeta essa migração?
5. Há rankings já publicados ou homologados afetados que precisem ser recalculados?

**Problema 2:**
6. O que significa exatamente "cartas": cartas de recomendação enviadas por terceiros ou documentos anexados pelo candidato?
7. Qual é o erro exibido hoje na submissão (mensagem, código ou stack trace)?
8. Onde a validação deve ocorrer: só no cadastro do edital, também na publicação, ou também na abertura das inscrições?
9. O que fazer com editais existentes que já exigem cartas e não têm modelo? Bloquear as inscrições, mostrar um aviso ou corrigir os dados?
10. Se o edital estiver inconsistente, o que o candidato deve ver ao tentar se inscrever?
11. Existe também um número máximo de cartas ou outra configuração relacionada que precise da mesma validação?

**Geral:**
12. Qual é a stack, quais são os comandos de build e teste, e em que estrutura de diretórios ficam esses módulos?
13. As duas correções devem ser entregues juntas ou separadamente? Alguma tem prioridade, por exemplo por haver um processo seletivo em andamento?