# Spec: Remoção de collation manual nos campos de autocomplete do processo seletivo

## Premissas

1. O projeto usa um banco de dados relacional com suporte a collation (provavelmente MySQL/MariaDB ou PostgreSQL). O SGBD exato não é citado na issue.
2. "Forçando collate" significa que as consultas dos campos de autocomplete aplicam uma cláusula `COLLATE` explícita (no SQL ou via ORM) para comparar corretamente textos com caracteres Unicode (acentos, cedilha etc.).
3. A "configuração nova do BD em produção" alterou o charset/collation padrão do banco, das tabelas ou das colunas para um padrão com suporte completo a Unicode (por exemplo, `utf8mb4` com collation insensível a acentos/caixa). Essa configuração ainda não foi confirmada.
4. O comportamento esperado do autocomplete se mantém: buscas com e sem acento e com diferença de maiúsculas/minúsculas devem continuar trazendo os mesmos resultados de hoje.
5. A collation forçada fica restrita à parte de "processo seletivo". Não se sabe se outras partes do sistema usam o mesmo recurso.
6. A entrega principal é uma **verificação**. A remoção do código só acontece se a verificação confirmar que é seguro.

## Objetivo

Verificar se a collation aplicada manualmente nas consultas dos campos de autocomplete do módulo de processo seletivo ainda é necessária depois da nova configuração do banco de dados em produção. Se não for, remover esse código.

**Por quê:** simplificar o código, eliminar um workaround que talvez esteja obsoleto e possivelmente melhorar o desempenho. Um `COLLATE` explícito pode impedir o uso de índices em algumas engines; isso ainda precisa ser confirmado.

**Usuários afetados:** quem usa os campos de autocomplete do processo seletivo (candidatos e/ou equipe administrativa; o perfil exato não é informado).

**Critérios de aceitação (alto nível):**
- Há uma conclusão documentada sobre a necessidade, ou não, da collation manual, com evidências da configuração do BD em produção.
- Se a remoção for viável, os autocompletes funcionam sem collation forçada e mantêm o mesmo comportamento com texto Unicode.
- Se não for viável, a issue registra o motivo e o código fica como está.

## Stack Tecnológica

Não informado na issue original. Linguagem, framework, ORM, SGBD e versões são desconhecidos.

## Comandos

Não informado na issue original.

- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Não informado na issue original. A issue só menciona a área funcional "processo seletivo" e os "campos de autocomplete". Arquivos, módulos e consultas envolvidos são desconhecidos.

## Estilo de Código

Não informado na issue original.

## Estratégia de Testes

Framework, localização dos testes e cobertura atual não constam na issue. Estratégia proposta, sem depender de ferramentas específicas:

1. **Verificação da configuração do BD:** comparar charset e collation do servidor, do banco, das tabelas e das colunas consultadas pelos autocompletes em produção e nos demais ambientes (dev, homologação, testes).
2. **Testes de comportamento do autocomplete,** antes e depois da remoção, com pelo menos estes casos:
   - termo sem acento encontrando registro com acento (ex.: "joao" → "João")
   - termo com acento encontrando registro sem acento, se esse for o comportamento atual
   - diferença de maiúsculas e minúsculas (ex.: "SÃO" → "São")
   - caracteres como "ç", "ñ" e "ü"
   - caracteres fora do BMP (ex.: emoji), se forem relevantes ao domínio
3. **Comparação de resultados:** para um conjunto de termos de busca, os resultados com e sem collation forçada devem ser idênticos no ambiente com a nova configuração.
4. **Regressão:** a suíte de testes existente deve continuar passando. O comando é desconhecido.

## Limites

- **Sempre:**
  - Confirmar a configuração real do BD em produção antes de remover qualquer código.
  - Garantir que os ambientes de dev, testes e homologação tenham configuração equivalente à de produção, ou registrar as diferenças.
  - Rodar os testes de comportamento Unicode antes e depois da alteração.
  - Restringir a mudança aos autocompletes do processo seletivo.
- **Perguntar antes:**
  - Alterar schema, charset ou collation de tabelas e colunas.
  - Remover collation forçada em outros módulos além do processo seletivo.
  - Mudar o comportamento de busca (por exemplo, passar a diferenciar acentos).
- **Nunca:**
  - Remover a collation sem evidência de que a configuração de produção a torna desnecessária.
  - Alterar a configuração do banco de produção como parte desta issue.
  - Remover ou desativar testes que falharem após a mudança sem aprovação.

## Critérios de Sucesso

1. Charset e collation do servidor, do banco, das tabelas e das colunas usadas pelos autocompletes estão documentados para produção e demais ambientes.
2. Todos os pontos de código do processo seletivo que forçam collation foram identificados e listados.
3. Para cada caso de teste Unicode da estratégia de testes, o autocomplete retorna os mesmos resultados com e sem a collation forçada, no ambiente com a nova configuração.
4. Uma destas decisões foi tomada e registrada:
   - **Remover:** o código de collation manual foi retirado, todos os testes passam e o comportamento é o mesmo; ou
   - **Manter:** a justificativa técnica está documentada na issue (por exemplo, uma coluna ou ambiente ainda sem a nova configuração).
5. Nenhuma regressão nos demais fluxos do processo seletivo.

## Perguntas em Aberto

1. Qual é o SGBD e qual é exatamente a "configuração nova" aplicada em produção (charset e collation de servidor, banco, tabelas e colunas)?
2. A nova configuração foi aplicada só ao banco/servidor, ou as tabelas e colunas existentes também foram convertidas? Colunas antigas podem manter a collation anterior.
3. Os ambientes de desenvolvimento, testes e homologação têm a mesma configuração de produção? Se não, a remoção pode quebrar esses ambientes.
4. Quais campos de autocomplete do processo seletivo usam collation forçada, e onde está esse código?
5. Qual é o comportamento esperado da busca: deve ignorar acentos e caixa? O comportamento atual deve ser preservado exatamente?
6. Outras partes do sistema forçam collation da mesma forma? Elas também devem ser avaliadas, ou o escopo é só o processo seletivo?
7. Houve algum problema concreto (bug ou desempenho) que motivou a issue, ou é apenas limpeza de código?
8. Existem testes automatizados para os autocompletes hoje? Qual framework e qual comando os executa?
9. Como "provavelmente não é mais necessário" será confirmado: há acesso de leitura às configurações do BD de produção, ou será preciso um ambiente que a replique?