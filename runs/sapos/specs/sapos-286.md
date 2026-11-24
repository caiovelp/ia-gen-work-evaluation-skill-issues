# Spec: Cancelamento automático das inscrições em disciplinas ao trancar uma matrícula

## Premissas
1. "Matrícula" é o vínculo do aluno com um curso/programa. "Inscrição em disciplina" é o registro do aluno em uma disciplina ou turma, associado a essa matrícula.
2. Uma matrícula pode ter várias inscrições em disciplinas, de períodos diferentes.
3. Só devem ser canceladas as inscrições ainda ativas ou em curso. Inscrições já concluídas, com nota, aprovação, reprovação ou já canceladas, ficam como estão.
4. O sistema já permite cancelar uma inscrição manualmente. O cancelamento automático deve ter o mesmo efeito que o manual, por exemplo liberar a vaga na turma ou mudar o status, incluindo os efeitos colaterais que o manual já tiver.
5. O trancamento já existe como funcionalidade. O pedido é só acrescentar o efeito de cancelar as inscrições automaticamente.
6. O trancamento e o cancelamento das inscrições devem ser atômicos: ou tudo acontece, ou nada acontece.
7. Os registros de inscrição não devem ser excluídos fisicamente. Eles devem ser marcados como cancelados, para manter o histórico.

## Objetivo
Hoje, quando a matrícula de um aluno é trancada, as inscrições dele nas disciplinas precisam ser canceladas manualmente. O objetivo é que, ao trancar uma matrícula, o sistema cancele sozinho as inscrições em disciplinas ligadas a ela.

**Usuário:** quem faz o trancamento de matrícula (por exemplo, a secretaria acadêmica). O perfil exato não consta da issue.

**Critérios de aceitação (proposta):**
- Ao trancar uma matrícula, todas as inscrições ativas dessa matrícula passam para o estado "cancelada", sem nenhuma ação manual.
- Inscrições de outras matrículas, inclusive de outras matrículas do mesmo aluno, não são afetadas.
- Inscrições que já estavam em estado final (concluída ou cancelada) não mudam.
- Se o cancelamento de alguma inscrição falhar, o trancamento não é efetivado e o erro é informado.
- Trancar uma matrícula sem inscrições ativas funciona normalmente, sem erro.

## Stack Tecnológica
Não informado na issue original.

## Comandos
Não informado na issue original.
- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto
Não informado na issue original.

## Estilo de Código
Não informado na issue original. Deve seguir as convenções já usadas no repositório, em especial no código que hoje faz o trancamento de matrícula e o cancelamento manual de inscrições.

## Estratégia de Testes
O framework e a localização dos testes não constam da issue. Proposta de cobertura:
- **Unitários/integração** da operação de trancamento:
  - matrícula com várias inscrições ativas → todas ficam canceladas;
  - matrícula com inscrições ativas e outras em estado final → só as ativas são canceladas;
  - matrícula sem inscrições → o trancamento acontece sem erro;
  - inscrições de outras matrículas permanecem iguais;
  - falha no meio do processo → nada é alterado (atomicidade).
- **Regressão:** o cancelamento manual de inscrição e o trancamento continuam funcionando como antes nos demais aspectos.

## Limites
- **Sempre:** reaproveitar a lógica do cancelamento manual que já existe, para manter os mesmos efeitos colaterais; executar o trancamento e os cancelamentos em uma única transação; rodar os testes antes de commitar.
- **Perguntar antes:** alterar o esquema do banco de dados (por exemplo, criar um novo status ou motivo de cancelamento); adicionar dependências; mudar o comportamento do destrancamento ou da reabertura da matrícula; enviar notificações a alunos ou professores.
- **Nunca:** excluir fisicamente os registros de inscrição; mexer em inscrições já concluídas ou com nota; cancelar inscrições de matrículas que não estão sendo trancadas.

## Critérios de Sucesso
- Depois de trancar uma matrícula pelo fluxo normal do sistema, nenhuma inscrição ativa ligada a ela continua ativa.
- O operador não precisa fazer nenhum passo manual para cancelar as inscrições.
- Os efeitos de cada inscrição cancelada automaticamente são iguais aos do cancelamento manual.
- Inscrições em estado final e inscrições de outras matrículas permanecem iguais.
- Os testes automatizados que cobrem os cenários acima passam.

## Questões em Aberto
1. Quais estados de inscrição contam como "ativos" e devem ser cancelados? Por exemplo: inscrita, em curso, pré-inscrição ou solicitação pendente.
2. O cancelamento vale só para as inscrições do período letivo corrente ou também para períodos futuros?
3. Deve existir um motivo ou status específico, como "cancelada por trancamento", diferente do cancelamento manual?
4. Ao destrancar a matrícula, as inscrições devem ser restauradas ou continuam canceladas?
5. O operador deve ver uma confirmação antes de trancar, listando as inscrições que serão canceladas?
6. Alguém deve ser notificado (aluno, professor, coordenação)?
7. O que fazer com inscrições que não podem ser canceladas por alguma regra de negócio, como prazo encerrado ou nota já lançada? O trancamento deve ser bloqueado ou essas inscrições devem ser ignoradas?
8. Existem outros jeitos de trancar uma matrícula (importação em lote, API, rotina agendada) que também precisam desse comportamento?
9. As inscrições que hoje estão ativas em matrículas já trancadas devem ser corrigidas retroativamente?
10. Quais são a stack, os comandos e a estrutura do projeto? Nenhum deles consta da issue.