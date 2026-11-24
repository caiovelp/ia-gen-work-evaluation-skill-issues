# Spec: Portaria de reconhecimento no "Conceito CAPES" do Histórico Escolar

## Objetivo

Mudar onde aparece a portaria de reconhecimento do curso no documento **"Histórico Escolar"**. Hoje ela fica no campo **"Curso"**. Passará a ficar no campo **"Conceito CAPES"**. A portaria exibida deve ser a do período avaliativo.

**Situação atual:**
- Campo "Curso": `Doutorado em Computação (Portaria MEC nº 398/2025)`

**Situação desejada:**
- Campo "Curso": `Doutorado em Computação`
- Campo "Conceito CAPES": `6 (Portaria MEC nº 398/2025)`

**Requisito adicional:** cada nível do conceito CAPES deve ficar associado à portaria que o publicou. Exemplo:
- Nível 5 → Portaria MEC nº 656/2017
- Nível 6 → Portaria MEC nº 609/2019

**Usuários afetados:**
- Discentes e egressos que recebem o Histórico Escolar.
- Secretaria ou coordenação do programa, que emite o documento.
- Terceiros que validam o documento.

**Critério de sucesso em alto nível:** o histórico exibe o conceito CAPES junto da portaria que o publicou, e o campo "Curso" deixa de conter a portaria.

## Premissas

1. O sistema já gera o "Histórico Escolar" e já tem os campos "Curso" e "Conceito CAPES".
2. Hoje a portaria fica em um único valor ligado ao curso. Por isso será preciso um novo registro, ou uma nova estrutura, que relacione cada nível de conceito à sua portaria.
3. Um curso pode ter vários conceitos CAPES ao longo do tempo, um por período avaliativo, cada um com sua portaria.
4. "Atualizar de acordo com o período avaliativo" significa exibir o conceito e a portaria vigentes no período relevante do discente. O período de referência exato está em aberto (ver Questões em Aberto).
5. O texto segue o padrão `<nível> (Portaria MEC nº <número>/<ano>)`, como nos exemplos da issue.
6. A mudança vale para todos os cursos e níveis, como mestrado e doutorado, e não só para o Doutorado em Computação do exemplo.
7. Os dados de conceitos e portarias serão cadastrados ou mantidos por um usuário administrativo. Não serão fixados no código.
8. Outros documentos que exibam a portaria no campo "Curso" (diplomas, declarações etc.) estão fora do escopo, salvo indicação contrária.

## Stack Tecnológica

Não informado na issue original.

## Comandos

Não informado na issue original.
- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Não informado na issue original. A localização do template do Histórico Escolar e do modelo de dados de curso e conceito CAPES é desconhecida.

## Estilo de Código

Não informado na issue original. Devem ser seguidas as convenções já existentes no repositório.

## Estratégia de Testes

Não informado na issue original. O framework e a localização dos testes são desconhecidos. Coberturas esperadas, a ajustar quando o repositório for conhecido:

- **Unidade:** dado um curso e um período de referência, é selecionado o conceito CAPES vigente e sua portaria correta.
- **Unidade:** formatação do texto `6 (Portaria MEC nº 398/2025)`.
- **Unidade/Integração:** o campo "Curso" é gerado sem a portaria.
- **Casos de borda:**
  - curso sem conceito cadastrado;
  - conceito sem portaria associada;
  - período de referência anterior ao primeiro conceito cadastrado;
  - troca de conceito no meio do período do discente.
- **Verificação manual/visual:** gerar o PDF ou documento do Histórico Escolar e conferir o layout. O texto maior no campo "Conceito CAPES" não deve quebrar a formatação.

## Limites

- **Sempre:**
  - manter o conteúdo dos demais campos do histórico inalterado;
  - preservar o formato textual da portaria (`Portaria MEC nº <número>/<ano>`);
  - executar os testes existentes antes de concluir.
- **Perguntar antes:**
  - alterações de esquema de banco de dados, como uma nova tabela ou relação de conceito × portaria × período;
  - migração ou carga dos dados históricos de conceitos e portarias;
  - alterações em outros documentos além do Histórico Escolar;
  - mudança no layout geral do documento.
- **Nunca:**
  - fixar portarias ou conceitos no código;
  - alterar históricos já emitidos ou assinados sem aprovação;
  - remover testes existentes.

## Critérios de Sucesso

1. No Histórico Escolar, o campo **"Curso"** exibe apenas o nome do curso, sem a portaria. Exemplo: `Doutorado em Computação`.
2. O campo **"Conceito CAPES"** exibe o nível seguido da portaria que o publicou. Exemplo: `6 (Portaria MEC nº 398/2025)`.
3. É possível registrar mais de um par nível/portaria por curso. Exemplo: nível 5 com a Portaria MEC nº 656/2017 e nível 6 com a Portaria MEC nº 609/2019.
4. O conceito e a portaria exibidos correspondem ao período avaliativo aplicável ao discente, segundo a regra definida nas Questões em Aberto.
5. Quando não houver portaria associada ao conceito, o documento é gerado sem erro, com o comportamento a definir.
6. Os documentos gerados para cursos de diferentes níveis (mestrado e doutorado) seguem o mesmo padrão.

## Questões em Aberto

1. **Período de referência:** qual período avaliativo define o conceito exibido? Opções:
   - o vigente na data de emissão do histórico;
   - o vigente na data de ingresso;
   - o vigente na data de conclusão ou defesa;
   - todos os conceitos vigentes durante o vínculo do discente.
2. **Múltiplos conceitos:** se o conceito mudou durante o curso do discente, o histórico mostra só um ou lista todos, como "Nível 5 (Portaria…) / Nível 6 (Portaria…)"?
3. **Tipo de portaria:** a portaria de exemplo (nº 398/2025) é de reconhecimento do curso, e as do requisito adicional são de publicação de conceito. Com a mudança, a portaria de reconhecimento deixa de aparecer, ou passa a ser a mesma que publica o conceito? Precisamos confirmar que se trata do mesmo dado.
4. **Inconsistência nos exemplos:** o primeiro exemplo associa o conceito 6 à Portaria nº 398/2025, e o segundo associa o nível 6 à Portaria nº 609/2019. Qual está correto, ou se referem a períodos diferentes?
5. **Cadastro dos dados:** já existe uma tela ou estrutura para cadastrar o histórico de conceitos CAPES por curso? Quem fará a carga dos dados históricos?
6. **Ausência de dados:** o que exibir quando o conceito não tiver portaria cadastrada? Apenas o nível, um texto padrão ou um bloqueio da emissão?
7. **Escopo:** a mudança vale apenas para o Histórico Escolar ou também para outros documentos que exibem a portaria, como declarações e diplomas?
8. **Documentos já emitidos:** devem permanecer como estão? Há versionamento ou validação por código ou QR que possa ser afetado?
9. **Grafia:** a issue usa ora "nº", ora "n°". Qual é a grafia oficial a adotar?