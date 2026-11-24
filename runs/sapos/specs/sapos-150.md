# Spec: Permitir buscar por bolsas suspensas na tela de alocação de bolsas

## Premissas

1. Existe no sistema uma **tela de alocação de bolsas** com algum mecanismo de busca ou filtro de bolsas.
2. O sistema já tem o conceito de **bolsa suspensa**, como um status, flag ou situação persistida. A issue não diz se isso existe hoje ou se precisa ser criado.
3. Hoje a busca da tela de alocação **não retorna** bolsas suspensas, ou não permite filtrar por elas. Por isso a funcionalidade foi pedida.
4. A mudança apenas **amplia a busca**. A regra de quais bolsas podem ser alocadas não muda, e não se assume que bolsas suspensas possam ser alocadas.
5. O comportamento padrão atual da busca, quando o usuário não escolhe a nova opção, deve continuar igual para não afetar quem já usa a tela.
6. Os perfis de usuário que já acessam a tela de alocação também poderão usar a nova busca, sem novas regras de permissão.

## Objetivo

Permitir que o usuário da tela de alocação de bolsas encontre **bolsas suspensas** pela busca dessa tela.

- **Usuário:** quem opera a tela de alocação de bolsas. O perfil exato não foi informado na issue.
- **Motivação:** não informada na issue original. O provável é que o usuário precise localizar bolsas suspensas para consultá-las ou agir sobre elas, e hoje elas não aparecem na busca.

**História de usuário:**
> Como usuário da tela de alocação de bolsas, quero buscar bolsas suspensas para localizá-las sem precisar de outra tela ou de outro meio.

## Stack Tecnológica

Não informado na issue original.

## Comandos

Não informado na issue original. Os comandos de build, teste, lint e execução local são desconhecidos.

## Estrutura do Projeto

Não informado na issue original. A localização da tela de alocação de bolsas, da lógica de busca e dos testes é desconhecida.

## Estilo de Código

Não informado na issue original. Deve-se seguir o padrão já usado no código da tela de alocação e da busca existente.

## Estratégia de Testes

O framework e a localização dos testes não foram informados na issue original. Os níveis esperados são:

- **Testes unitários ou de integração da busca:**
  - com o critério "suspensas" ativo, bolsas suspensas são retornadas;
  - com o critério ausente, o resultado é idêntico ao comportamento atual (teste de regressão);
  - a nova opção combina corretamente com os demais filtros já existentes na tela.
- **Teste de interface ou ponta a ponta (se houver no projeto):** o usuário seleciona a opção na tela de alocação e vê as bolsas suspensas na listagem.

## Limites

- **Sempre:**
  - manter o comportamento padrão atual da busca quando a nova opção não for usada;
  - seguir as convenções do código existente;
  - incluir testes para o novo critério e para a regressão do comportamento atual.
- **Perguntar antes:**
  - alterar o esquema do banco de dados, por exemplo para criar um status de suspensão caso não exista;
  - mudar as regras de alocação, como permitir alocar bolsas suspensas;
  - alterar permissões de acesso;
  - adicionar dependências.
- **Nunca:**
  - alterar o status de bolsas como efeito colateral da busca;
  - remover ou desativar testes existentes sem aprovação;
  - expor bolsas suspensas a perfis que hoje não têm acesso a elas.

## Critérios de Sucesso

1. A tela de alocação de bolsas oferece uma forma de buscar ou filtrar **bolsas suspensas**. O formato do controle está pendente: ver Perguntas em Aberto.
2. Com essa opção ativa, a busca retorna as bolsas cujo status é "suspensa" e que atendem aos demais critérios informados.
3. Sem essa opção, a busca retorna exatamente o mesmo resultado de antes da mudança.
4. Cada bolsa suspensa listada é identificável como suspensa no resultado. Isso depende de validação: ver Perguntas em Aberto.
5. O comportamento das ações de alocação sobre bolsas suspensas segue a regra definida pelo produto, também pendente de validação.
6. Os testes automatizados cobrindo os pontos 2 e 3 passam.

## Perguntas em Aberto

1. **Definição de "suspensa":** existe hoje um status ou campo que marca a bolsa como suspensa? Qual é o nome ou valor exato?
2. **Comportamento atual:** hoje as bolsas suspensas são excluídas da busca, ou a busca simplesmente não oferece um filtro para elas?
3. **Formato do controle na tela:** como o usuário deve ativar a busca?
   - (a) um filtro de status que inclua "suspensa";
   - (b) uma opção que acrescenta as suspensas aos resultados;
   - (c) uma opção que mostra apenas as suspensas.
4. **Ações permitidas:** depois de encontrar uma bolsa suspensa na tela, o usuário pode alocá-la, reativá-la ou alterá-la? Ou ela aparece só para consulta?
5. **Identificação visual:** as bolsas suspensas devem ter indicação visual nos resultados, como uma etiqueta ou cor?
6. **Outros status:** existem outros status, como cancelada ou encerrada, que também deveriam ser buscáveis? Ou o escopo é só "suspensa"?
7. **Permissões:** todos os perfis com acesso à tela de alocação podem ver bolsas suspensas?
8. **Dados exibidos:** é preciso mostrar informações sobre a suspensão, como data, motivo ou responsável?
9. **Stack, comandos, estrutura do projeto e estilo de código:** não informados na issue original. São necessários para completar a spec.