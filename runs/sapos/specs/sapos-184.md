# Spec: Busca na tela de Desligamentos

## Objetivo

Ampliar os filtros de busca da tela de Desligamentos. Hoje a tela não oferece todos os critérios de que os usuários precisam. Serão incluídos três novos filtros:

1. **Ano**
2. **Tipo de desligamento**
3. **Nível da matrícula**

**Usuário:** quem consulta registros de desligamento nessa tela. O perfil exato não foi informado na issue.

**Por quê:** permitir localizar desligamentos com mais precisão e rapidez, sem depender só dos filtros atuais.

**Histórias de usuário:**
- Como usuário da tela de Desligamentos, quero filtrar por **ano** para ver apenas os desligamentos de um período.
- Como usuário da tela de Desligamentos, quero filtrar por **tipo de desligamento** para analisar um tipo específico.
- Como usuário da tela de Desligamentos, quero filtrar por **nível da matrícula** para restringir os resultados a um nível.

## Premissas

1. A tela de Desligamentos já existe e já tem algum mecanismo de busca/filtro. Os novos campos serão acrescentados a ele, sem substituí-lo.
2. Os filtros existentes continuam funcionando como hoje.
3. Os filtros são combináveis entre si e com os já existentes, usando lógica **E** (AND).
4. Todos os novos campos são **opcionais**. Campo vazio não restringe o resultado.
5. "Ano" se refere ao ano da **data do desligamento**, e não ao ano de admissão, de matrícula ou de outra data.
6. "Ano" é um valor único, sem intervalo de anos.
7. "Tipo de desligamento" e "nível da matrícula" já existem como dados estruturados no sistema, de preferência como listas de valores pré-definidos. Por isso serão exibidos como campos de seleção, e não como texto livre.
8. Cada um desses dois filtros aceita **um único valor** por busca, sem seleção múltipla.
9. A filtragem é feita no mesmo lugar da busca atual (servidor ou cliente, o que já for usado), respeitando a paginação existente, se houver.
10. Não há mudança de permissões. Quem já acessa a tela pode usar os novos filtros.
11. Não é necessária alteração de esquema de banco de dados.

## Stack Tecnológica

Não informado na issue original. Linguagem, framework, banco de dados e versões são desconhecidos.

## Comandos

Não informado na issue original.

- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Não informado na issue original. A localização da tela de Desligamentos, da camada de consulta/API e dos testes é desconhecida.

## Estilo de Código

Não informado na issue original. Seguir as convenções já usadas na tela de Desligamentos e nos filtros existentes.

## Estratégia de Testes

O framework e a localização dos testes não foram informados na issue original. Níveis de teste esperados, sujeitos ao que o projeto já usa:

- **Unitário/integração (consulta):**
  - filtro por ano;
  - filtro por tipo;
  - filtro por nível;
  - combinações entre os três;
  - combinação com os filtros existentes;
  - campos vazios não restringem o resultado;
  - combinação que não retorna nenhum resultado.
- **Interface:** os três campos aparecem, são preenchíveis/selecionáveis e disparam a busca. A ação de limpar filtros, se existir, reinicia os novos campos.
- **Regressão:** os filtros existentes continuam retornando os mesmos resultados de antes.

## Limites

- **Sempre:**
  - manter o comportamento dos filtros existentes;
  - tratar os novos campos como opcionais;
  - validar a entrada (ano numérico de 4 dígitos);
  - seguir o padrão visual e de código da tela atual;
  - rodar os testes antes de commitar.
- **Perguntar antes:**
  - alterar o esquema do banco ou criar índices;
  - adicionar dependências;
  - mudar o contrato de API usado por outros consumidores;
  - mudar as permissões de acesso à tela;
  - alterar ou remover filtros já existentes.
- **Nunca:**
  - remover filtros existentes sem aprovação;
  - commitar segredos;
  - remover ou desativar testes que estejam falhando sem aprovação.

## Critérios de Sucesso

1. A tela de Desligamentos exibe três novos campos de busca: **Ano**, **Tipo de desligamento** e **Nível da matrícula**.
2. Ao informar um ano, apenas desligamentos cuja data de desligamento pertence a esse ano são exibidos.
3. Ao selecionar um tipo, apenas desligamentos desse tipo são exibidos.
4. Ao selecionar um nível, apenas desligamentos de matrículas desse nível são exibidos.
5. Ao combinar os novos filtros entre si e com os existentes, o resultado atende a **todos** os critérios informados.
6. Com os novos campos vazios, o resultado é idêntico ao da busca atual (sem regressão).
7. As opções de "Tipo de desligamento" e "Nível da matrícula" refletem os valores existentes no sistema.
8. Um ano inválido (não numérico ou fora do formato) não é aceito ou gera mensagem de validação clara.
9. Uma busca sem resultados exibe o estado vazio já usado pela tela.
10. A paginação e a ordenação existentes, se houver, continuam corretas com os novos filtros aplicados.
11. Os testes automatizados cobrindo os itens acima passam.

## Questões em Aberto

1. **Ano de quê?** É o ano da data de desligamento ou de outra data (admissão, matrícula, competência)?
2. **Ano único ou intervalo?** Basta um ano ou deve ser possível informar de/até?
3. **Tipos de desligamento:** quais valores existem e de onde vêm (tabela de domínio, enum, texto livre)?
4. **Nível da matrícula:** o que é exatamente o "nível" e quais valores possui? Ele está associado à matrícula no momento do desligamento ou ao estado atual?
5. **Seleção múltipla:** os filtros de tipo e nível devem permitir mais de um valor ao mesmo tempo?
6. **Filtros atuais:** quais filtros a tela já possui? A filtragem é feita no servidor ou no cliente?
7. **Valores padrão:** algum dos novos campos deve vir preenchido por padrão (por exemplo, o ano corrente)?
8. **Persistência:** os filtros devem ser mantidos ao navegar ou ser refletidos na URL, para compartilhamento?
9. **Exportação/relatórios:** se a tela tiver exportação, ela deve respeitar os novos filtros?
10. **Volume de dados e desempenho:** há metas de tempo de resposta? Pode ser necessário criar índices para esses campos?
11. **Permissões:** algum dos novos filtros expõe informação restrita a determinados perfis?