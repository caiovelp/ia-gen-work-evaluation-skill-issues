# Spec: Linhas de Pesquisa dentro de Áreas de Pesquisa (SAPOS)

## Objetivo

Criar no SAPOS o conceito de **Linha de Pesquisa**, subordinado ao conceito existente de **Área de Pesquisa**. Assim é possível registrar a linha de pesquisa de cada aluno.

**Contexto:** hoje o SAPOS tem apenas o campo "área de pesquisa". O programa tinha 7 áreas. Agora tem uma única área (Ciência da Computação), e as 7 áreas antigas passaram a ser linhas de pesquisa. O conceito "área de pesquisa" não pode ser reaproveitado para representar linhas, porque ele aparece no histórico do aluno no campo "área de concentração".

**Usuários:**
- Usuários administrativos do SAPOS que cadastram áreas, linhas e matrículas.
- Indiretamente, os alunos, cujo histórico e cuja matrícula passam a refletir a linha.

**Modelagem sugerida (prof. Leonardo Murta):** relação todo-parte análoga à de País/Estado já existente no SAPOS. A Área é o todo e a Linha é a parte. Cada linha pertence a exatamente uma área.

**Histórias de usuário:**
1. Como administrador, quero cadastrar uma linha de pesquisa indicando a área a que ela pertence, para organizar as linhas do programa.
2. Como administrador, quero listar, editar e remover linhas de pesquisa, da mesma forma que faço com Estados de um País.
3. Como administrador, ao cadastrar ou editar uma matrícula, quero indicar a linha de pesquisa do aluno. As opções devem ficar restritas às linhas da área selecionada.
4. Como programa, quero que o histórico continue exibindo a área de concentração a partir da Área de Pesquisa, sem regressão.

**Alternativas para a matrícula (a decidir):**
- **(A)** A matrícula indica somente a linha, e a área é inferida a partir dela.
- **(B)** Manter o campo "área de concentração" e adicionar o campo "linha de pesquisa", filtrado pela área selecionada. O autor indica esta opção como mais fácil para a migração.

## Premissas

1. O SAPOS já possui um modelo de Área de Pesquisa e um modelo País/Estado com relação todo-parte. Este último serve de referência de implementação.
2. A opção **(B)** será adotada, por facilitar a migração. A matrícula mantém a "área de concentração" e ganha o campo "linha de pesquisa", com filtro dependente da área.
3. O campo "linha de pesquisa" na matrícula é **opcional**, para não invalidar matrículas existentes sem linha.
4. Uma linha pertence a **exatamente uma** área. A área é obrigatória na linha.
5. O nome da linha é único **dentro da mesma área**.
6. O histórico continua usando a Área de Pesquisa para "área de concentração". Exibir a linha no histórico está fora do escopo, salvo decisão em contrário.
7. Não haverá migração automática dos dados antigos (as 7 áreas viram 7 linhas). A conversão, se desejada, é feita manualmente ou fica para trabalho separado.
8. A remoção de uma área com linhas associadas, ou de uma linha associada a matrículas, deve ser bloqueada ou tratada com o mesmo comportamento já usado para País/Estado.
9. As permissões de acesso ao cadastro de linhas seguem as do cadastro de áreas de pesquisa.

## Stack Tecnológica

Não informado na issue original. Supõe-se a mesma stack já usada pelo SAPOS; versões e dependências são desconhecidas.

## Comandos

Não informado na issue original.
- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido
- Migrações de banco: desconhecido

## Estrutura do Projeto

Não informado na issue original. Os caminhos dos modelos existentes (Área de Pesquisa, País, Estado, Matrícula, Histórico) e dos respectivos testes são desconhecidos. A implementação deve espelhar a organização usada para País/Estado.

## Estilo de Código

Não informado na issue original. Seguir as convenções do código existente, em particular a implementação de País/Estado como modelo de referência. Isso vale para nomenclatura, validações, telas de cadastro e campos dependentes.

## Estratégia de Testes

Não informado na issue original (framework, localização dos testes e cobertura desconhecidos). Níveis mínimos esperados:

- **Modelo:**
  - Linha exige área.
  - Linha exige nome.
  - Unicidade do nome dentro da mesma área.
  - A associação Área → Linhas funciona.
- **Matrícula:**
  - É possível salvar com e sem linha.
  - É rejeitada uma linha que não pertence à área selecionada.
- **Interface/integração:**
  - O seletor de linha na matrícula mostra apenas as linhas da área selecionada.
  - O seletor de linha se atualiza ao trocar a área.
- **Regressão:** o histórico continua exibindo a "área de concentração" corretamente.
- **Migração:** matrículas existentes permanecem válidas após a alteração do esquema.

## Limites

- **Sempre:**
  - Seguir o padrão de País/Estado.
  - Manter compatibilidade com matrículas e históricos existentes.
  - Validar a consistência linha ↔ área.
  - Executar os testes antes de commitar.
- **Perguntar antes:**
  - Alterar o esquema de matrícula de forma que torne a linha obrigatória.
  - Migrar dados existentes (converter áreas antigas em linhas).
  - Alterar o conteúdo ou o layout do histórico.
  - Adicionar dependências.
  - Remover o campo "área de concentração".
- **Nunca:**
  - Reaproveitar ou renomear o conceito "área de pesquisa" para representar linhas.
  - Quebrar a geração do histórico.
  - Apagar dados de áreas ou matrículas existentes.

## Critérios de Sucesso

1. Existe o conceito Linha de Pesquisa, com nome e área obrigatórios, gerenciável por tela de cadastro com operações de criar, listar, editar e remover.
2. Ao cadastrar uma linha, o usuário escolhe a área a que ela pertence.
3. A tela de Área de Pesquisa permite visualizar as linhas associadas, se esse for o padrão em País/Estado.
4. A matrícula possui o campo "linha de pesquisa":
   - O campo é opcional.
   - As opções ficam limitadas às linhas da "área de concentração" selecionada.
   - O campo é atualizado quando a área muda.
5. Salvar uma matrícula com uma linha de outra área resulta em erro de validação.
6. Matrículas existentes continuam válidas e editáveis após a mudança, sem preencher a linha.
7. O histórico continua exibindo a "área de concentração" como antes.
8. A remoção de áreas ou linhas em uso não deixa referências órfãs.

## Questões em Aberto

1. **Opção A ou B:** a matrícula indica só a linha (área inferida) ou mantém a área e adiciona a linha filtrada? Esta spec assume B. A opção A seria adotada no futuro, após a migração?
2. A linha de pesquisa deve ser **obrigatória** em novas matrículas?
3. A linha de pesquisa deve aparecer no **histórico** ou em outros relatórios e documentos? Em quais?
4. Deve haver **migração automática** das 7 áreas antigas para linhas da área "Ciência da Computação", reatribuindo as matrículas existentes?
5. Qual o comportamento esperado ao remover uma área com linhas, ou uma linha vinculada a matrículas: bloquear, cascata ou anular?
6. A linha de pesquisa também deve ser associada a **professores/orientadores** ou a outras entidades além da matrícula?
7. Quais atributos a linha deve ter além do nome (ex.: código, descrição, status ativo/inativo)?
8. Quais perfis de usuário podem gerenciar linhas de pesquisa?
9. Uma linha pode mudar de área depois de criada, e o que acontece com as matrículas já vinculadas nesse caso?
10. Stack, comandos de build e teste, e estrutura de diretórios do SAPOS: não informados na issue.