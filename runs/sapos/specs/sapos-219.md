# Especificação: Inscrição online no processo seletivo de mestrado e doutorado

## Objetivo

Permitir que candidatos aos cursos de **mestrado e doutorado** da pós-graduação do IC/UFF façam a inscrição no processo seletivo pelo sistema, em vez de usar o formulário em PDF.

**Usuários:**
- **Candidato:** preenche o formulário e envia a documentação exigida.
- **Secretaria / comissão de seleção (presumido):** consulta as inscrições recebidas.

**Referências citadas na issue (conteúdo não verificado, pois não houve acesso aos links):**
- Regras e documentação exigida: http://www.ic.uff.br/index.php/pt/pos-graduacao/inscricoes
- Formulário de inscrição em uso: http://www.ic.uff.br/images/documentos/pos_graduacao/formularios_e_requerimentos/formulario_inscricao.pdf

**Requisitos explícitos da issue:**
1. O candidato se inscreve online no processo seletivo de mestrado ou doutorado.
2. A inscrição segue as regras e a documentação exigida na página de inscrições do IC/UFF.
3. O formulário online tem os campos do formulário de inscrição atual (PDF).
4. O candidato escolhe o idioma de preenchimento: português, inglês ou outro.
5. A funcionalidade se relaciona com a issue #157 (carta de recomendação).

**Histórias de usuário (derivadas):**
- Como candidato, quero escolher mestrado ou doutorado e preencher o formulário online, para não precisar imprimir, preencher e enviar um PDF.
- Como candidato, quero preencher o formulário em português ou em inglês, para me inscrever mesmo sem dominar o português.
- Como candidato, quero anexar os documentos exigidos na própria inscrição, para concluí-la em um só lugar.
- Como membro da secretaria ou da comissão, quero ver as inscrições recebidas com os documentos, para avaliar os candidatos.

## Premissas

1. O sistema já existe. Esta issue pertence a um repositório de software do IC/UFF que ainda não conheço.
2. A inscrição é feita por uma interface web.
3. Os campos do formulário online equivalem aos do PDF atual. A lista exata de campos não foi verificada.
4. A "documentação exigida" é enviada como anexo (upload de arquivos) no momento da inscrição.
5. "Escolher a língua" pode significar duas coisas, a confirmar:
   - **(a)** traduzir a interface e os rótulos do formulário; ou
   - **(b)** registrar em que idioma o candidato escreveu as respostas livres.
   Assumo (a) com pelo menos português e inglês, e registro também o idioma escolhido junto da inscrição.
6. A carta de recomendação (issue #157) é uma funcionalidade separada. Esta especificação só prevê o ponto de ligação entre a inscrição e a carta, sem implementar a carta.
7. Mestrado e doutorado usam o mesmo fluxo, com possíveis diferenças de campos ou documentos.
8. Existe o conceito de "processo seletivo" (edital ou período) ao qual cada inscrição pertence.

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

Não informado na issue original.

Diretriz geral, a ajustar ao framework do projeto (desconhecido):
- **Testes unitários:** validação de campos obrigatórios e de anexos (tipo e tamanho).
- **Testes de integração:** gravação da inscrição e dos anexos, e vínculo com o processo seletivo.
- **Testes de fluxo ponta a ponta:**
  - inscrição completa para mestrado e para doutorado;
  - troca de idioma pt/en.

## Limites

- **Sempre:**
  - validar no servidor os dados e os arquivos enviados;
  - proteger os dados pessoais dos candidatos, conforme a LGPD;
  - seguir as convenções existentes do projeto;
  - rodar os testes antes de commits.
- **Perguntar antes:**
  - alterar o esquema do banco de dados;
  - adicionar dependências, como bibliotecas de internacionalização ou upload;
  - definir o comportamento integrado à carta de recomendação (#157);
  - mudar regras de negócio do processo seletivo.
- **Nunca:**
  - expor documentos ou dados pessoais de candidatos a usuários não autorizados;
  - commitar segredos ou credenciais;
  - remover testes que falham sem aprovação.

## Critérios de Sucesso

1. O candidato acessa a página de inscrição e escolhe o nível: mestrado ou doutorado.
2. O formulário online contém todos os campos do formulário de inscrição em PDF. A lista será validada pela secretaria.
3. O candidato escolhe o idioma (no mínimo português e inglês). Todos os rótulos, instruções e mensagens de validação aparecem no idioma escolhido.
4. O idioma escolhido fica registrado na inscrição.
5. O candidato anexa todos os documentos exigidos para o nível escolhido. A inscrição não é concluída se faltar algum documento obrigatório.
6. Campos obrigatórios em branco ou inválidos impedem o envio e geram mensagem clara no idioma escolhido.
7. Ao concluir, o candidato recebe uma confirmação de que a inscrição foi registrada. A forma (tela, e-mail ou protocolo) está a definir.
8. Cada inscrição fica associada a um processo seletivo específico.
9. Inscrições fora do período do processo seletivo são bloqueadas, se houver período definido.
10. Secretaria ou comissão consegue listar as inscrições e acessar os dados e anexos de cada uma.
11. A inscrição expõe o necessário para a issue #157 associar cartas de recomendação ao candidato, como um identificador e os dados dos recomendantes, se aplicável.

## Questões em Aberto

1. **Idioma:** "outra língua" significa um terceiro idioma específico (qual?) ou só português e inglês por enquanto? A escolha de idioma muda a interface, o idioma das respostas, ou ambos?
2. **Campos:** a lista de campos do PDF continua válida? Há campos diferentes para mestrado e doutorado?
3. **Documentos:**
   - Quais documentos são exigidos para cada nível?
   - Quais formatos são aceitos (só PDF?) e qual o tamanho máximo?
   - Algum documento é opcional?
4. **Issue #157:**
   - Os recomendantes são informados pelo candidato no formulário de inscrição?
   - O sistema deve disparar o pedido de carta a partir da inscrição?
   - A inscrição só fica completa depois que as cartas chegam?
5. **Autenticação do candidato:** o candidato precisa criar conta e fazer login? Pode salvar um rascunho e voltar depois? Pode editar a inscrição após o envio?
6. **Processo seletivo:**
   - O sistema já modela editais ou períodos de inscrição?
   - Quem os cria e configura?
   - Há vagas, linhas de pesquisa ou orientadores a escolher no formulário?
7. **Taxa de inscrição:** existe taxa ou isenção a tratar no fluxo?
8. **Confirmação:** como o candidato é notificado (e-mail, número de protocolo, comprovante em PDF)?
9. **Visualização pela secretaria:** quem tem acesso às inscrições? É preciso exportar (planilha, PDF consolidado)?
10. **Dados pessoais:** qual a política de retenção e privacidade dos documentos dos candidatos (LGPD)?
11. **Escopo:** a issue junta várias capacidades testáveis de forma independente: formulário de inscrição, envio de documentos, internacionalização e integração com a carta de recomendação. Convém dividi-la em módulos ou sub-issues antes de detalhar cada uma?
12. **Projeto:** quais são a stack, os comandos de build e teste, a estrutura de diretórios e as convenções de código? Nada disso consta na issue.