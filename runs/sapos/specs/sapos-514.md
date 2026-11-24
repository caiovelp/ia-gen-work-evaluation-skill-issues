# Spec: Corrigir erro de subject longo no e-mail de lançamento de nota

## Objetivo

O lançamento de nota falha quando o nome da turma é muito longo. O erro é:

```
Mysql2::Error: Data too long for column 'subject' at row 1
```

**Causa identificada na issue:** o nome da turma entra no assunto (subject) do e-mail enviado ao aluno, ao professor e ao orientador. O texto resultante ultrapassa o tamanho da coluna `subject`.

**Solução escolhida na issue:** o subject deve conter apenas o nome da disciplina, sem o nome da turma.

**Usuários afetados:**
- Quem lança notas (provavelmente professores ou a secretaria).
- Quem recebe os e-mails: aluno, professor e orientador.

**Critérios de aceitação (história):**
- Como usuário que lança notas, quero lançar a nota de uma turma com nome muito longo sem erro, para que o registro seja concluído.
- Como aluno, professor ou orientador, quero receber o e-mail de notificação com o nome da disciplina no assunto.

## Premissas

1. A aplicação é Ruby on Rails com banco MySQL. Isso é inferido pelo erro `Mysql2::Error`, que vem da gem `mysql2`.
2. A coluna `subject` pertence a uma tabela que registra ou enfileira os e-mails enviados, por exemplo um log de notificações. Nome da tabela e do modelo desconhecidos.
3. O erro acontece porque o e-mail é gravado no banco na mesma operação do lançamento. Por isso a falha impede o lançamento da nota.
4. Os três e-mails (aluno, professor e orientador) são montados no mesmo fluxo e usam o nome da turma no subject.
5. "Nome da disciplina" é um atributo próprio da disciplina, separado do nome da turma.
6. O nome da disciplina, somado ao texto fixo do subject, cabe no limite atual da coluna. Esse limite não foi informado.
7. O esquema do banco não será alterado, porque a solução escolhida foi mudar o conteúdo do subject.
8. O corpo do e-mail não muda. Ele pode continuar mostrando o nome da turma.

## Stack Tecnológica

- Linguagem/framework: provavelmente Ruby on Rails (inferido, não confirmado).
- Banco de dados: MySQL, via adapter `mysql2`.
- Versões: Não informado na issue original.

## Comandos

Não informado na issue original.

- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Não informado na issue original.

Arquivos que provavelmente precisarão ser alterados (localização desconhecida):
- Onde o subject dos e-mails de lançamento de nota é montado (mailer, notificação ou equivalente) para aluno, professor e orientador.
- Testes desse fluxo de envio.

## Estilo de Código

Não informado na issue original. Seguir as convenções já usadas no código existente de e-mails e notificações.

## Estratégia de Testes

Framework e localização dos testes: Não informado na issue original.

Cenários que precisam de cobertura:
- **Regressão:** lançar nota em uma turma com nome longo, maior que o limite da coluna `subject`, não gera erro, e a nota fica registrada.
- **Conteúdo do subject:** os e-mails para aluno, professor e orientador têm o nome da disciplina no subject e não têm o nome da turma.
- **Caso normal:** o lançamento em turma com nome curto continua funcionando e envia os três e-mails.
- **Destinatários:** aluno, professor e orientador continuam recebendo o e-mail.

## Limites

- **Sempre:**
  - Rodar a suíte de testes existente antes de commitar.
  - Aplicar a mudança aos três e-mails (aluno, professor e orientador).
  - Adicionar um teste de regressão com nome de turma longo.
- **Perguntar antes:**
  - Alterar o esquema do banco, como aumentar a coluna `subject` ou mudar seu tipo.
  - Truncar o subject em vez de só trocar o conteúdo.
  - Mudar o corpo do e-mail ou outros e-mails que também usam o nome da turma no subject.
  - Adicionar dependências.
- **Nunca:**
  - Engolir ou ignorar a exceção para "resolver" o erro.
  - Deixar o lançamento da nota falhar silenciosamente.
  - Remover testes existentes sem aprovação.

## Critérios de Sucesso

1. Lançar nota em turma com nome longo conclui sem `Mysql2::Error: Data too long for column 'subject'`.
2. A nota fica persistida corretamente nesse cenário.
3. Os subjects dos e-mails para aluno, professor e orientador contêm o nome da disciplina e não contêm o nome da turma.
4. Os três destinatários continuam recebendo o e-mail.
5. Há um teste automatizado que reproduz o cenário do nome longo. Ele falha antes da correção e passa depois.
6. Os testes existentes continuam passando.

## Perguntas em Aberto

1. Qual é o tamanho máximo da coluna `subject`, e em qual tabela ou modelo ela está?
2. O nome da disciplina também pode ser longo o bastante para estourar o limite? Se puder, devemos truncar o subject por precaução ou aumentar a coluna?
3. Qual é o formato exato desejado para o novo subject? Existe um prefixo ou texto fixo, por exemplo "Nota lançada – {disciplina}"?
4. O subject deve continuar igual para os três destinatários, ou cada um tem um texto diferente?
5. Outros e-mails do sistema também usam o nome da turma no subject e podem ter o mesmo problema? Devem entrar no escopo desta correção?
6. O nome da turma deve continuar aparecendo no corpo do e-mail, para o destinatário saber de qual turma se trata?
7. A falha no registro ou envio do e-mail deve continuar impedindo o lançamento da nota, ou o lançamento deve ser independente da notificação?
8. Quais são os comandos de build e teste e qual é o framework de testes do projeto?