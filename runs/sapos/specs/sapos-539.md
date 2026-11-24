# Especificação: Exemplo padrão de processo seletivo (modelo do IC)

## Objetivo

Criar um **processo seletivo de exemplo, configurado por padrão**, que replique o processo usado atualmente no IC. O exemplo serve de ponto de partida para que outros programas e desenvolvedores entendam a funcionalidade de edital seletivo e a adaptem às suas necessidades.

**Usuários-alvo:**
- Programas que adotarem o sistema e queiram um edital funcional para adaptar.
- Desenvolvedores que precisam de dados realistas para entender ou testar a funcionalidade.

**Como o exemplo é criado:** a issue menciona "a migração". Portanto, o exemplo deve ser criado por uma migração de dados (ver Premissas e Questões em Aberto).

**O que o exemplo deve conter:**

1. **Edital de seleção**
   - Formulário de candidatura **sem carta** (de recomendação).
   - Duas fases, nesta ordem: **Homologação** e **Avaliação**.

2. **Ranking padrão**
   - Seletores: "Ampla concorrência", "Racial" e "PcD".
   - Ordenação: "Nota final" e, depois, "Média da formação acadêmica".

3. **Ranking de bolsas**
   - Um único seletor.
   - Condição: o candidato solicitou bolsa.
   - Ordenação: os mesmos critérios do ranking padrão.

4. **Fase de Homologação**
   - Formulário com os campos:
     - "Optante negro ou indígena"
     - "PcD"
     - "Homologação"
     - "Razão de indeferimento"
   - Consolidação: envio de e-mail de notificação de **deferimento** ou de **indeferimento**.
   - Condição de aprovação: `"Homologação" = "Deferida"`.
   - Comitê: um único usuário com papel de **secretaria**. Se não existir nenhum, usar o usuário **admin**.

5. **Fase de Avaliação**
   - Formulário com os campos:
     - "Nota da formação acadêmica"
     - "Nota da experiência acadêmica e profissional"
     - "Observação"
   - Consolidação: cálculo de:
     - "Média da formação acadêmica"
     - "Média da experiência acadêmica e profissional"
     - "Nota final"
   - Condição de aprovação: `"Nota final" >= 6`.
   - Comitê: usuário **admin**. O ideal seriam professores, mas o admin foi escolhido por ser mais "seguro" numa configuração padrão.

## Premissas

1. O sistema já tem os conceitos de edital, fases, formulários de fase, consolidação, condição de aprovação, comitê, ranking, seletores, ordenação e notificação por e-mail. A issue só pede **dados de configuração**, sem novas funcionalidades.
2. "Migração" significa uma migração de dados do framework usado no projeto. O framework não é informado.
3. "Sem carta" significa que o formulário de candidatura não exige carta de recomendação.
4. O campo "Homologação" é de escolha, com pelo menos as opções "Deferida" e "Indeferida".
5. "Razão de indeferimento" é texto livre, relevante apenas quando a homologação é "Indeferida".
6. "Optante negro ou indígena" e "PcD" são campos booleanos (sim/não) preenchidos pela secretaria na homologação.
7. Esses dois campos alimentam os seletores "Racial" e "PcD" do ranking padrão.
8. "Nota final" e "Média da formação acadêmica" são critérios em ordem: o primeiro é o principal e o segundo é o desempate. Ambos são decrescentes.
9. As médias são calculadas a partir das notas dadas pelos membros do comitê de avaliação.
10. O formulário de candidatura já tem, ou terá, um campo que indica se o candidato solicitou bolsa.
11. Existe um usuário admin identificável de forma determinística.
12. A migração deve ser segura para reexecução e para bancos já populados: não deve duplicar o exemplo nem falhar.

## Stack Tecnológica

Não informado na issue original.

## Comandos

Não informado na issue original. Os comandos de build, teste, lint e execução de migrações são desconhecidos.

## Estrutura do Projeto

Não informado na issue original. A localização das migrações, dos modelos de edital e ranking e dos templates de e-mail é desconhecida.

## Estilo de Código

Não informado na issue original.

## Estratégia de Testes

O framework de testes não é informado na issue original. Os níveis de teste desejados são:

- **Teste de migração:** em banco vazio e em banco com dados, a migração cria exatamente um edital de exemplo com todas as configurações listadas no Objetivo.
- **Teste de comitê – Homologação:**
  - Com usuário(s) de papel secretaria, o comitê contém exatamente 1 deles.
  - Sem secretaria, o comitê contém o admin.
- **Teste de comitê – Avaliação:** o comitê contém o admin.
- **Teste de condição – Homologação:** "Deferida" aprova e "Indeferida" reprova.
- **Teste de condição – Avaliação:**
  - "Nota final" = 6 aprova.
  - "Nota final" < 6 reprova.
- **Teste de consolidação:** médias e "Nota final" calculadas corretamente (depende da fórmula; ver Questões em Aberto).
- **Teste de rankings:**
  - Os seletores filtram corretamente.
  - A ordenação usa "Nota final" e, depois, "Média da formação acadêmica".
  - O ranking de bolsas inclui apenas quem solicitou bolsa.
- **Teste de notificação:** a consolidação da homologação dispara o e-mail correto (deferimento ou indeferimento).
- **Teste de reexecução:** rodar a migração novamente não duplica dados.

## Limites

- **Sempre:**
  - Usar as funcionalidades existentes de edital e ranking, sem criar mecanismos paralelos.
  - Manter os nomes de campos e seletores exatamente como na issue.
  - Garantir que a migração seja reversível e idempotente, se o framework permitir.
  - Rodar os testes antes de commitar.
- **Perguntar antes:**
  - Alterar o esquema do banco ou os modelos existentes para viabilizar o exemplo.
  - Adicionar dependências.
  - Definir pesos ou fórmula da "Nota final" não descritos na issue.
  - Publicar ou ativar o edital de exemplo por padrão.
- **Nunca:**
  - Criar usuários novos com credenciais fixas.
  - Expor dados pessoais reais nos textos de exemplo ou nos e-mails.
  - Alterar ou remover editais existentes durante a migração.

## Critérios de Sucesso

1. Após rodar as migrações em um banco novo, existe um edital de exemplo com:
   - formulário de candidatura sem carta;
   - as fases "Homologação" e "Avaliação", nesta ordem.
2. A fase de Homologação tem:
   - os 4 campos especificados;
   - consolidação com e-mail de deferimento e de indeferimento;
   - condição `"Homologação" = "Deferida"`;
   - comitê com exatamente 1 usuário secretaria ou, na falta dele, o admin.
3. A fase de Avaliação tem:
   - os 3 campos especificados;
   - consolidação que calcula as 3 métricas;
   - condição `"Nota final" >= 6`;
   - comitê com o admin.
4. O ranking padrão tem os seletores "Ampla concorrência", "Racial" e "PcD", ordenados por "Nota final" e depois por "Média da formação acadêmica".
5. O ranking de bolsas tem um único seletor, inclui apenas candidatos que solicitaram bolsa e usa a mesma ordenação.
6. Rodar a migração em um banco que já tem dados, incluindo outros editais, não quebra nem altera registros existentes.
7. Um desenvolvedor consegue duplicar ou editar o exemplo pela interface ou pelo fluxo existente para customizá-lo.
8. Todos os testes listados na Estratégia de Testes passam.

## Questões em Aberto

1. **Mecanismo de criação:** deve ser uma migração de dados, uma *fixture* ou *seed*, ou um comando de gerenciamento? A issue diz "migração". Ela deve rodar automaticamente em todos os ambientes, inclusive em produção?
2. **Fórmula da "Nota final":** é a média simples das duas médias, ou há pesos? Como lidar com notas ausentes?
3. **Cálculo das médias:** são a média aritmética entre os avaliadores do comitê?
4. **Escala das notas:** a escala é de 0 a 10? Há casas decimais? Há validação de faixa no formulário?
5. **Campo "Homologação":** as opções são só "Deferida" e "Indeferida"?
6. **"Razão de indeferimento":** é obrigatória quando a homologação é "Indeferida"?
7. **Seletores do ranking padrão:**
   - "Ampla concorrência" inclui todos os candidatos ou só os não optantes?
   - Um candidato pode aparecer em mais de um seletor?
   - Há número de vagas por seletor?
8. **"Solicitou bolsa":** esse campo já existe no formulário de candidatura? Se não, deve ser criado no exemplo?
9. **Seletor do ranking de bolsas:** qual o nome dele?
10. **Conteúdo dos e-mails:** qual o texto, o assunto e o remetente dos e-mails de deferimento e indeferimento? Existem templates prontos? A razão de indeferimento deve ser incluída no e-mail?
11. **Escolha do usuário secretaria:** qual critério usar para escolher "1 só" quando há vários (ex.: o mais antigo, o menor ID)?
12. **Identificação do admin:** como identificar "o admin" (username fixo, superusuário, papel)? O que fazer se nem admin nem secretaria existirem?
13. **Estado do edital:** o edital de exemplo deve ser criado como rascunho, inativo ou publicado? Que datas de abertura e fechamento usar?
14. **Programa associado:** o exemplo deve ficar vinculado a algum programa ou curso específico (ex.: IC)?
15. **Outros campos da candidatura:** quais outros campos, além da ausência de carta, o formulário de candidatura do IC possui hoje?
16. **Reversão:** ao reverter a migração, o exemplo deve ser removido, mesmo que já tenha sido customizado ou tenha candidaturas?