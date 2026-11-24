# Spec: Histórico de Credenciamento de Professores

## Objetivo

Registrar a **data de credenciamento** de cada professor e guardar o **histórico completo** de credenciamentos e descredenciamentos. Um professor pode se credenciar, ser descredenciado e se credenciar de novo quantas vezes for preciso. Cada ciclo precisa ficar registrado, sem sobrescrever os anteriores.

**Usuários:** Não informado na issue original. Supõe-se que sejam os administradores ou a secretaria que gerenciam o cadastro de professores.

**Critérios de aceitação (derivados da issue):**
- O sistema guarda a data em que o professor foi credenciado.
- O sistema guarda a data em que o professor foi descredenciado.
- Um professor pode ter um número ilimitado de ciclos de credenciamento/descredenciamento.
- Um novo credenciamento não apaga nem altera os registros anteriores.
- É possível consultar o histórico completo de um professor.

## Premissas

1. Já existe no sistema uma entidade "Professor" persistida em banco de dados.
2. O histórico será modelado como uma coleção de períodos (por exemplo, data de início e data de fim opcional) ligada ao professor, e não como campos únicos na entidade Professor.
3. Um professor tem **no máximo um** período de credenciamento ativo (sem data de fim) por vez.
4. Os períodos de um mesmo professor não se sobrepõem.
5. O professor é considerado "credenciado" quando tem um período ativo. Se já existir um campo de status, ele precisa ficar coerente com o histórico.
6. As datas são de calendário (dia), sem hora. A confirmar.
7. A data de descredenciamento não pode ser anterior à data de credenciamento do mesmo período.
8. Credenciamentos anteriores a esta funcionalidade, se existirem, precisarão de alguma estratégia de migração. A estratégia está em aberto.

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

Não informado na issue original.

## Estratégia de Testes

Framework e localização dos testes não informados na issue original. Cenários que precisam de cobertura, independentemente do framework:

- Credenciar um professor que nunca foi credenciado cria um período ativo com a data informada.
- Descredenciar um professor credenciado encerra o período ativo com a data informada.
- Recredenciar um professor descredenciado cria um **novo** período e preserva os anteriores.
- Vários ciclos seguidos (por exemplo, 3 ou mais) resultam em um histórico ordenado e completo.
- Tentar credenciar um professor já credenciado é rejeitado (ver Perguntas em Aberto).
- Tentar descredenciar um professor que não está credenciado é rejeitado.
- Uma data de descredenciamento anterior à data de credenciamento é rejeitada.
- A consulta do histórico retorna os períodos em ordem cronológica.

## Limites

- **Sempre:**
  - Preservar os registros históricos: nunca sobrescrever ou apagar períodos anteriores ao recredenciar.
  - Validar a consistência das datas e dos estados (sem sobreposição, fim ≥ início, no máximo um período ativo).
  - Escrever testes para os cenários de ciclo múltiplo.
- **Perguntar antes:**
  - Alterar o esquema do banco de dados (nova tabela ou coleção para o histórico).
  - Migrar ou converter dados de credenciamento existentes.
  - Remover ou alterar campos atuais de status do professor.
  - Adicionar dependências.
- **Nunca:**
  - Apagar o histórico de credenciamento de um professor como efeito colateral de outra operação.
  - Permitir que o histórico seja editado silenciosamente sem uma regra definida.

## Critérios de Sucesso

- [ ] Cada professor tem um histórico com zero ou mais períodos de credenciamento.
- [ ] Cada período registra a data de credenciamento e, quando houver, a data de descredenciamento.
- [ ] Recredenciar cria um novo período sem alterar os anteriores.
- [ ] Não existe limite artificial para o número de ciclos.
- [ ] Nunca há mais de um período ativo por professor.
- [ ] A data de credenciamento atual (do período ativo) pode ser consultada facilmente.
- [ ] O histórico completo pode ser consultado em ordem cronológica.
- [ ] Todos os cenários listados em "Estratégia de Testes" passam.

## Perguntas em Aberto

1. **Onde o histórico aparece?** Ele deve ser exibido na interface (tela do professor), exposto via API, ou os dois? Também falta definir se é preciso relatório ou exportação.
2. **Data de descredenciamento:** a issue cita apenas a "data de credenciamento". Confirmar que a data de descredenciamento também deve ser registrada. Isso parece necessário para o histórico fazer sentido.
3. **Motivo e responsável:** devemos registrar o motivo do descredenciamento, quem executou a ação ou observações?
4. **Edição e correção:** um período já registrado pode ser editado ou excluído (por exemplo, em caso de erro de digitação)? Se puder, quem pode fazer isso e a alteração deve ser auditada?
5. **Datas retroativas ou futuras:** é permitido registrar credenciamentos com data passada ou futura, ou a data é sempre a do momento da ação?
6. **Dados existentes:** já existem professores credenciados no sistema? Se existirem, qual data de credenciamento inicial eles devem receber (data de cadastro, data desconhecida, preenchimento manual)?
7. **Status atual:** já existe um campo de status ou flag "credenciado" no professor? Ele deve continuar existindo, derivado do histórico, ou ser substituído?
8. **Credenciamento duplicado:** o que fazer ao tentar credenciar um professor já credenciado: rejeitar com erro ou ignorar?
9. **Granularidade:** a informação é só a data (dia) ou também o horário?
10. **Tipos de credenciamento:** existe mais de uma modalidade de credenciamento (por exemplo, por programa, curso ou categoria)? Se existir, o histórico precisa separá-las?
11. **Stack, comandos e estrutura do projeto:** não informados. São necessários para completar as seções técnicas desta spec.