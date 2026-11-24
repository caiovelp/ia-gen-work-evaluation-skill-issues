# Spec: Identificação visual por curso e mensagem de e-mail não encontrado no SAPOS

## Objetivo

Um usuário fez uma busca no Google, clicou num link do SAPOS e caiu na instância de um curso diferente do seu (o dele é "computação"). Ali, o login e a redefinição de senha falharam várias vezes porque o e-mail dele não está cadastrado naquela instância. Nada na tela indicava que ele estava no curso errado.

Queremos que o usuário perceba rapidamente que está na instância de outro curso. A issue sugere duas abordagens, que podem ser adotadas juntas ou separadas:

1. **Identificação visual por curso:** a tela de login e as telas de acesso de cada curso mostram com clareza a qual curso a instância pertence.
2. **Mensagem orientativa:** quando o e-mail não é encontrado no login ou na redefinição de senha, o sistema avisa que o e-mail não foi identificado e que o usuário pode estar acessando o curso errado.

**Usuários:** quem acessa o SAPOS (alunos e possivelmente docentes e secretaria), sobretudo quem chega por links externos, como resultados de busca.

**Histórias de usuário:**
- Como usuário que chegou por um link externo, quero ver na tela de login a qual curso aquela instância pertence, para saber se estou no lugar certo antes de tentar entrar.
- Como usuário cujo e-mail não existe na instância acessada, quero uma mensagem que sugira que posso estar no curso errado, para não ficar tentando login e redefinição de senha sem sucesso.

## Premissas

1. Pelo relato, o SAPOS roda em instâncias, URLs ou configurações separadas por curso, cada uma com sua própria base de usuários.
2. O curso da instância (nome e talvez sigla) está disponível em alguma configuração que pode ser exibida na interface.
3. Os pontos de contato afetados são pelo menos a tela de login e o fluxo de "esqueci minha senha".
4. Hoje, quando o e-mail não é encontrado, o sistema mostra uma mensagem genérica ou nenhuma que aponte o curso errado como causa provável.
5. Não está claro se o usuário viu alguma mensagem de erro, nem qual. Isso fica como questão em aberto.
6. A mudança não altera regras de autenticação, só a apresentação e as mensagens.

## Stack Tecnológica

Não informado na issue original.

## Comandos

Não informado na issue original.
- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Não informado na issue original. Não se sabe onde ficam as views de login e redefinição de senha, os arquivos de configuração por instância ou curso, nem os arquivos de tradução e mensagens.

## Estilo de Código

Não informado na issue original.

## Estratégia de Testes

Não informado na issue original. O framework e a localização dos testes são desconhecidos. Níveis sugeridos, a confirmar:
- **Teste de view ou integração:** a tela de login e a de redefinição de senha mostram o nome ou a identificação do curso configurado.
- **Teste de integração do fluxo de redefinição de senha:** um e-mail inexistente gera a mensagem orientativa.
- **Teste de integração do login:** credenciais com e-mail inexistente geram a mensagem combinada (ver questões de segurança abaixo).
- **Verificação manual:** comparar duas instâncias de cursos diferentes e confirmar que se distinguem visualmente.

## Limites

- **Sempre:**
  - Exibir a identificação do curso a partir da configuração da instância, sem valores fixos no código.
  - Manter os textos na mesma língua e no mesmo mecanismo de internacionalização já usados no projeto, se houver.
  - Rodar os testes existentes antes de commitar.
- **Perguntar antes:**
  - Mudar o comportamento de segurança das mensagens de login e redefinição de senha. Revelar se um e-mail existe ou não pode permitir enumeração de usuários.
  - Adicionar novos campos de configuração por instância, como cor, logotipo ou nome do curso.
  - Adicionar dependências ou mudar o esquema do banco de dados.
  - Criar uma página central para escolher o curso, que vai além do escopo pedido.
- **Nunca:**
  - Relaxar regras de autenticação ou de redefinição de senha.
  - Expor dados de usuários de outros cursos ou instâncias.
  - Commitar segredos ou credenciais de instâncias.

## Critérios de Sucesso

- [ ] A tela de login de cada instância mostra o nome do curso configurado de forma visível, sem rolar a página.
- [ ] A tela de redefinição de senha também mostra o nome do curso.
- [ ] Duas instâncias de cursos diferentes se distinguem visualmente (no mínimo pelo nome do curso, e talvez por cor ou logotipo, a decidir).
- [ ] Quando o e-mail informado na redefinição de senha não pertence à instância, a mensagem diz algo como: "Não identificamos este e-mail no curso X. Verifique se você está acessando o sistema do curso correto." O texto exato depende da decisão de segurança.
- [ ] Quando o login falha, a mensagem de erro lembra o usuário de confirmar que está no sistema do curso correto e cita o nome do curso.
- [ ] Os fluxos de login e redefinição de senha continuam funcionando como antes para usuários válidos.

## Questões em Aberto

1. **Arquitetura:** o SAPOS roda como instâncias separadas por curso (deploys, domínios ou bancos distintos) ou como uma instância só com vários cursos? Isso define onde fica a identificação do curso.
2. **Segurança e enumeração de e-mails:** pode-se dizer explicitamente que o e-mail não foi encontrado? A alternativa é uma mensagem neutra, como "Se este e-mail estiver cadastrado no curso X, você receberá…", junto com o lembrete sobre o curso errado.
3. **Escopo visual:** basta mostrar o nome do curso no cabeçalho e na tela de login, ou cada curso deve ter identidade visual própria (cor, logotipo, tema)? Quem fornece esses recursos?
4. **Mensagem atual:** o que o sistema mostra hoje quando o e-mail não é encontrado no login e na redefinição de senha? O usuário recebeu algum erro ou nenhum retorno?
5. **Escopo da entrega:** as duas sugestões entram juntas ou separadas? São capacidades que podem ser testadas de forma independente e poderiam virar specs distintas.
6. **Navegação entre cursos:** a mensagem deve apontar para os demais cursos, por exemplo com uma lista de links para as outras instâncias? Se sim, de onde vem essa lista?
7. **Indexação:** vale tratar a origem do problema, ou seja, como o Google indexa as instâncias (títulos e descrições das páginas com o nome do curso)? Ou isso fica fora do escopo?
8. **Idiomas:** as mensagens precisam de tradução além do português?