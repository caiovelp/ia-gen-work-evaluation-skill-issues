# Spec: Permitir desligamento por desistência durante o período de trancamento de matrícula

## Objetivo

Hoje o SAPOS impede o registro de um desligamento por desistência quando a data cai dentro de um período em que a matrícula do aluno está trancada. A issue traz uma captura de tela da tela de bloqueio, mas o texto do erro não aparece no conteúdo disponível.

A Coordenação do Curso orientou que o sistema seja verificado e ajustado para aceitar esse desligamento durante o trancamento.

**Usuário:** quem opera o SAPOS e registra desligamentos, como secretaria ou coordenação. O perfil exato não foi informado.

**Como seria o sucesso:** o operador consegue registrar o desligamento por desistência de um aluno com matrícula trancada. Os dados de matrícula, trancamento e desligamento continuam consistentes.

**História de usuário:**
> Como operador do SAPOS, quero registrar o desligamento por desistência de um aluno cuja matrícula está trancada, para que a situação acadêmica reflita a decisão do aluno e da Coordenação sem precisar esperar o fim do trancamento.

## Premissas

1. A operação bloqueada é o registro de um desligamento com motivo "desistência" para uma matrícula que tem um trancamento cobrindo a data do desligamento.
2. O bloqueio vem de uma regra de validação do sistema, e não de falha inesperada ou bug de interface. A mensagem exata está só na imagem.
3. A mudança vale apenas para o motivo "desistência". Os demais motivos de desligamento continuam bloqueados durante o trancamento, a menos que se decida o contrário (ver Questões em Aberto).
4. "Configuração do sistema" na issue pode significar mudança de regra no código ou ajuste de parâmetro já existente. Não se sabe qual dos dois.
5. Fora a liberação do desligamento, nenhuma regra de trancamento muda, como prazos, limites de semestres ou relatórios.
6. Desligamentos e trancamentos já registrados não serão alterados retroativamente.

## Stack Tecnológica

Não informado na issue original.

## Comandos

Não informado na issue original.

- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Não informado na issue original. Não se sabe onde ficam a validação de desligamento, o modelo de trancamento nem os testes.

## Estilo de Código

Não informado na issue original.

## Estratégia de Testes

Não informado na issue original. O framework e a localização dos testes são desconhecidos.

Os testes deverão cobrir pelo menos os cenários dos Critérios de Sucesso:
- desligamento por desistência dentro do trancamento (permitido);
- outros motivos dentro do trancamento (comportamento a confirmar);
- desligamento fora de trancamento (sem regressão).

## Limites

- **Sempre:**
  - Preservar as validações existentes de desligamento que não dizem respeito ao trancamento.
  - Cobrir o novo comportamento com testes automatizados.
  - Manter o comportamento atual para os motivos de desligamento não incluídos no escopo.
- **Perguntar antes:**
  - Alterar o esquema do banco de dados.
  - Criar novo parâmetro de configuração.
  - Mudar automaticamente as datas de trancamentos existentes, como encerrar o trancamento na data do desligamento.
  - Estender a liberação a outros motivos de desligamento.
  - Mudar relatórios ou documentos emitidos.
- **Nunca:**
  - Remover a validação de trancamento de forma global, sem restringir ao motivo desistência.
  - Alterar dados de produção.
  - Remover testes existentes que falhem sem aprovação.

## Critérios de Sucesso

1. Um aluno tem matrícula trancada em um período que cobre a data D. Ao registrar desligamento por desistência com data D, o sistema salva o registro sem erro.
2. Para motivos de desligamento diferentes de desistência, o comportamento durante o trancamento segue a decisão tomada nas Questões em Aberto. Por padrão, continua igual ao atual.
3. O desligamento por desistência fora de qualquer período de trancamento continua funcionando como antes.
4. Depois do desligamento, a situação da matrícula aparece como desligada em todas as telas e listagens em que hoje aparece como trancada ou ativa. O tratamento do trancamento sobreposto segue a decisão da Questão 4.
5. Existem testes automatizados para os critérios 1 a 3, e a suíte completa passa.

## Questões em Aberto

1. **Mensagem e local do bloqueio:** qual é o texto exato do erro mostrado na captura de tela, e em qual tela ele aparece? Isso permite localizar a regra.
2. **Abrangência dos motivos:** a liberação vale só para "desistência" ou também para outros motivos, como abandono, prazo esgotado ou a pedido? Existe uma lista oficial de motivos permitidos durante o trancamento?
3. **Configurável ou fixo:** a regra deve ser fixa no sistema ou configurável, por exemplo uma marcação por motivo de desligamento indicando se ele é permitido durante o trancamento? A issue fala em "configuração do sistema".
4. **Trancamento sobreposto:** o que fazer com o trancamento que continua vigente após a data do desligamento? As opções são:
   - mantê-lo como está;
   - encerrá-lo automaticamente na data do desligamento;
   - exigir que o operador o encerre manualmente antes.
5. **Data do desligamento:** pode ser qualquer data dentro do trancamento, ou deve coincidir com o início ou o fim do período? Desligamentos retroativos são permitidos?
6. **Efeitos colaterais:** o desligamento durante o trancamento afeta o cálculo de prazos, bolsas, relatórios ou documentos, como declarações e histórico? Algum deles precisa tratar esse caso de forma especial?
7. **Permissões:** quais perfis de usuário podem fazer esse desligamento? São os mesmos que já registram desligamentos hoje?
8. **Normativa:** existe regulamento do programa ou da instituição que respalde formalmente essa mudança e que deva ser referenciado?