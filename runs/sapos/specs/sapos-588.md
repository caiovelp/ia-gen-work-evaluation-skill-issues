# Especificação: Bloquear a emissão de documentos para aluno avulso por usuários com perfil de professor ou aluno

## Objetivo

**Problema relatado:** professores estão conseguindo gerar boletins assinados digitalmente para alunos avulsos diretamente no Sapos. Isso não deveria ser possível.

**O que queremos:**
- Nenhum usuário com perfil de **professor** ou de **aluno** deve conseguir gerar documento para aluno avulso. Isso inclui boletim, histórico e declarações, assinados digitalmente ou não. Ver Q1 em Perguntas em aberto.
- Somente usuários da **coordenação** ou da **secretaria** podem emitir documentos para aluno avulso, como a declaração de aluno avulso.

**Primeiro passo obrigatório: validar o problema.** Antes de qualquer alteração, é preciso reproduzir o comportamento relatado e levantar as restrições que existem hoje em cada ponto de emissão:
1. Os ícones de **histórico** e **boletim** na visualização/listagem de alunos.
2. A **tabela de declarações** que aparece ao clicar no "olhinho" (visualizar) de um aluno.

**Usuários afetados:**
- **Coordenação / Secretaria:** continuam emitindo documentos para alunos avulsos normalmente.
- **Professor / Aluno:** deixam de conseguir emitir documentos para alunos avulsos.
- **Aluno avulso:** é quem recebe o documento. Só deve recebê-lo se ele for emitido pela coordenação ou pela secretaria.

**Critérios de aceitação (histórias):**
- Como professor, ao visualizar um aluno avulso, não vejo nem consigo acionar a geração de boletim, histórico ou declaração.
- Como aluno, não consigo gerar nenhum documento referente a um aluno avulso, inclusive o meu próprio, caso eu seja avulso. Ver Q3.
- Como coordenação ou secretaria, continuo conseguindo emitir declarações, histórico e boletim para alunos avulsos.
- A restrição vale no servidor e não depende apenas de esconder ícones. Requisições diretas à URL de geração também são negadas.

## Premissas
1. O "Sapos" é a aplicação web de gestão acadêmica onde o problema ocorre, e o controle de acesso é feito por perfis de usuário (professor, aluno, coordenação, secretaria e possivelmente outros).
2. Existe no sistema uma forma de identificar que um aluno/matrícula é "avulso", por exemplo um nível, tipo de matrícula ou flag. O mecanismo exato é desconhecido.
3. Os pontos de emissão citados na issue (ícones de histórico/boletim e tabela de declarações) são os principais caminhos de geração. Podem existir outros, como rotas diretas, ações em lote ou API, que também precisam ser cobertos.
4. A regra deve ser aplicada na autorização do servidor, não apenas na interface. Esconder ícones sozinho não resolve o problema.
5. "Qualquer documento" (título da issue) prevalece sobre "assinado digitalmente" (corpo da issue). O bloqueio cobre documentos com e sem assinatura digital. Ver Q1.
6. O comportamento para alunos **não avulsos** não muda. Professores e alunos mantêm as permissões atuais sobre alunos regulares.
7. Documentos já emitidos indevidamente no passado estão fora do escopo desta issue. Ver Q5.
8. As imagens anexadas à issue (ícones e tabela de declarações) não puderam ser consultadas. A descrição delas foi inferida do texto.

## Stack tecnológica
Não informado na issue original.

## Comandos
Não informado na issue original. Os comandos de build, teste, lint e execução local são desconhecidos.

## Estrutura do projeto
Não informado na issue original. A localização dos controllers, das regras de permissão, das views de alunos e da geração de documentos/declarações é desconhecida e precisa ser levantada na etapa de validação.

## Estilo de código
Não informado na issue original. Seguir as convenções já existentes no repositório, em especial o mecanismo de autorização por perfil já em uso.

## Estratégia de testes
O framework e a localização dos testes não foram informados na issue original. As preocupações que precisam de cobertura são:
- **Autorização (unidade/regra de permissão):** para cada combinação de perfil (professor, aluno, coordenação, secretaria) × tipo de aluno (avulso, regular) × documento (boletim, histórico, declaração), verificar se a geração é permitida ou negada.
- **Requisição/integração:** chamadas diretas aos endpoints de geração de boletim, histórico e declaração para um aluno avulso, feitas com perfil de professor ou aluno, são negadas.
- **Interface:** os ícones de histórico/boletim e as ações da tabela de declarações não aparecem para professor ou aluno quando o aluno é avulso, e aparecem para coordenação e secretaria.
- **Regressão:** a emissão para alunos regulares continua funcionando para todos os perfis que já tinham acesso.

## Limites
- **Sempre:**
  - Validar e documentar o comportamento atual antes de alterar código: quais restrições existem hoje em cada ponto de emissão e para quais perfis.
  - Aplicar a restrição no servidor, além da interface.
  - Cobrir todos os pontos de emissão encontrados, não só os dois citados na issue.
  - Rodar a suíte de testes existente antes de concluir.
- **Perguntar antes:**
  - Alterar o modelo de dados, por exemplo criar uma flag de "avulso" se ela não existir.
  - Mudar permissões de perfis além de professor e aluno, como administrador ou outros.
  - Alterar o comportamento para alunos regulares.
  - Invalidar ou revogar documentos já emitidos.
- **Nunca:**
  - Resolver apenas escondendo ícones, deixando a rota de geração acessível.
  - Remover ou afrouxar permissões da coordenação ou da secretaria para alunos avulsos.
  - Remover testes existentes que falharem sem aprovação.

## Critérios de sucesso
1. **Validação documentada:** existe um registro, por exemplo um comentário na issue, que descreve:
   - para cada perfil, quais documentos ele consegue gerar hoje para aluno avulso;
   - por qual caminho isso acontece: ícones de histórico/boletim, tabela de declarações ou outros.

   O registro confirma ou refuta o problema relatado.
2. Um usuário com perfil **professor** não consegue gerar boletim, histórico nem declaração para aluno avulso:
   - os ícones e ações não aparecem;
   - uma requisição direta é negada.
3. Um usuário com perfil **aluno** não consegue gerar boletim, histórico nem declaração para aluno avulso, nas mesmas condições do item 2.
4. Usuários com perfil **coordenação** e **secretaria** continuam conseguindo emitir declarações (incluindo a declaração de aluno avulso), histórico e boletim para alunos avulsos.
5. Para alunos **não avulsos**, as permissões de todos os perfis permanecem idênticas às atuais.
6. Existem testes automatizados que cobrem a matriz perfil × tipo de aluno × documento descrita na Estratégia de testes, e todos passam.

## Perguntas em aberto
1. **Escopo do bloqueio:** o título da issue fala em "qualquer documento", e o corpo fala em documento "assinado digitalmente". Documentos sem assinatura digital, como uma pré-visualização ou PDF simples, também devem ser bloqueados para professor e aluno?
2. **Definição de "aluno avulso":** como o sistema identifica um aluno avulso hoje? É um nível, um tipo de matrícula, um campo específico? Um aluno pode ser avulso em uma matrícula e regular em outra? Nesse caso, a regra vale por matrícula ou por pessoa?
3. **Próprio aluno avulso:** o aluno avulso, logado com perfil de aluno, também deve ser impedido de gerar os próprios documentos? A leitura literal da issue indica que sim.
4. **Outros perfis:** além de coordenação e secretaria, há outros perfis (administrador, suporte etc.) que devem manter ou perder acesso à emissão para alunos avulsos?
5. **Documentos já emitidos:** boletins assinados que professores já geraram para alunos avulsos devem ser identificados, invalidados ou auditados? Isso faz parte desta issue ou de outra?
6. **Outros pontos de emissão:** além dos ícones de histórico/boletim e da tabela de declarações, há outros caminhos de geração (rotas diretas, ações em lote, API, envio por e-mail) que devem ser verificados?
7. **Visibilidade vs. geração:** professores e alunos devem continuar **vendo** a tabela de declarações e os dados do aluno avulso, apenas sem poder gerar documentos? Ou a visualização também deve ser restrita?
8. **Feedback ao usuário:** quando um professor ou aluno tentar gerar um documento por acesso direto, que mensagem ou comportamento é esperado: erro de permissão, redirecionamento ou outro?