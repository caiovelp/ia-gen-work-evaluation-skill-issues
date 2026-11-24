# Spec: Envio de boletim anexado na notificação

## Premissas

1. "Sapos" é o sistema onde a funcionalidade existe e onde os alunos já conseguem obter o próprio boletim. A plataforma e a stack não são informadas na issue.
2. A mudança recente nos "mecanismos de geração de boletim" introduziu boletins com QR Code. A geração com QR Code parece envolver o armazenamento de cada boletim gerado, possivelmente para validação de autenticidade. Isso foi inferido do texto da issue e não está confirmado.
3. A opção na tela de notificação é uma seleção (checkbox ou similar) visível na imagem anexada à issue. O nome exato do campo e da opção não está legível no texto da issue.
4. Uma notificação pode ser enviada para muitos alunos de uma vez ("centenas de boletins de uma só vez").
5. O defeito acontece em toda notificação com a opção ativada, e não apenas em casos específicos. Não há mensagem de erro nem log na issue.
6. As duas soluções propostas na issue são alternativas excludentes. Só uma delas será implementada.

## Objetivo

Resolver o defeito no envio de boletim anexado à notificação. Hoje, ao marcar a opção de anexar boletim, o boletim não é gerado ou não é anexado. O problema começou depois da mudança nos mecanismos de geração de boletim.

**Usuários afetados:**
- Quem cria e envia notificações no Sapos (provavelmente administração ou secretaria; não confirmado).
- Os alunos que recebem as notificações.

**Duas alternativas foram propostas na issue (a decidir):**

- **Alternativa A: remover a opção.** Retirar da notificação a seleção de "enviar boletim", porque os alunos já conseguem obter o boletim diretamente no Sapos.
- **Alternativa B: gerar sem QR Code.** Manter a opção, mas anexar um boletim sem QR Code, destinado apenas à conferência do aluno. Esse boletim não seria armazenado, o que evita persistir centenas de boletins de uma só vez.

**Critério de sucesso geral:** nenhuma notificação deve falhar ou ser enviada de forma inconsistente por causa da opção de boletim.

## Stack tecnológica

Não informado na issue original.

## Comandos

Não informado na issue original.

- Build: desconhecido
- Teste: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do projeto

Não informado na issue original. Os arquivos envolvidos ainda precisam ser identificados:
- tela ou formulário de notificação;
- lógica de envio de notificação;
- geração de boletim, nas versões antiga e nova.

## Estilo de código

Não informado na issue original.

## Estratégia de testes

O framework e a localização dos testes não foram informados na issue original. Níveis de teste esperados:

- **Reprodução do defeito:** um teste que envia uma notificação com a opção de boletim ativada e mostra a falha atual, antes de qualquer correção.
- **Alternativa A:**
  - Teste verificando que a opção não aparece mais no formulário de notificação.
  - Teste verificando que notificações antigas, que tinham a opção ativada, não quebram ao ser processadas ou exibidas.
- **Alternativa B:**
  - Teste verificando que o anexo é gerado sem QR Code.
  - Teste verificando que nenhum registro ou arquivo de boletim é persistido.
  - Teste verificando que o envio para vários destinatários anexa o boletim correto de cada aluno.
- **Regressão:** a geração de boletim com QR Code pelo próprio aluno no Sapos continua funcionando como hoje.

## Limites

- **Sempre:**
  - Reproduzir o defeito antes de corrigir.
  - Preservar o fluxo atual de geração de boletim com QR Code feita pelo aluno no Sapos.
  - Garantir que notificações sem a opção de boletim continuem funcionando.
- **Perguntar antes:**
  - Remover a opção, ou seja, adotar a Alternativa A.
  - Alterar o esquema do banco de dados, por exemplo para remover um campo ou flag da notificação.
  - Alterar o mecanismo novo de geração de boletim.
  - Mudar o comportamento de notificações já agendadas ou já existentes com a opção ativada.
- **Nunca:**
  - Armazenar em massa boletins com QR Code a partir do envio de notificações.
  - Remover testes existentes de geração de boletim sem aprovação.

## Critérios de sucesso

**Comuns às duas alternativas:**
- [ ] A causa do defeito está identificada e documentada, ou seja, o que mudou no mecanismo de geração que quebrou o envio.
- [ ] Enviar uma notificação no Sapos não gera erro em nenhuma configuração da tela de notificação.
- [ ] A geração de boletim pelo aluno no Sapos, com QR Code, continua funcionando sem regressões.

**Se a Alternativa A for escolhida:**
- [ ] A seleção de envio de boletim não aparece mais no formulário de notificação.
- [ ] Notificações existentes com a opção ativada são tratadas sem erro. Como tratar ainda está a definir; ver Questões em aberto.

**Se a Alternativa B for escolhida:**
- [ ] Com a opção ativada, cada aluno destinatário recebe o próprio boletim em anexo.
- [ ] O boletim anexado não contém QR Code.
- [ ] Nenhum boletim gerado para a notificação é armazenado de forma persistente.
- [ ] O documento deixa claro que serve apenas para conferência e não é um documento oficial. O texto exato ainda está a definir.
- [ ] O envio para muitos destinatários, na ordem de centenas, termina sem falha. A meta de tempo e de recursos ainda está a definir.

## Questões em aberto

1. **Qual alternativa adotar: A (remover a opção) ou B (gerar sem QR Code)?** Esta é a decisão principal e bloqueia o restante da spec.
2. Qual é exatamente o sintoma atual? As possibilidades são:
   - erro na tela;
   - notificação enviada sem anexo;
   - notificação que não é enviada;
   - exceção registrada em log.

   Há mensagens de erro ou logs disponíveis?
3. Qual mudança específica no mecanismo de geração de boletim causou a quebra? Em que versão ou commit ela entrou?
4. A geração com QR Code obriga a armazenar o boletim, por exemplo para validação pública? E a geração sem QR Code dispensa esse armazenamento?
5. **Se for a Alternativa A:**
   - O que fazer com notificações já cadastradas, agendadas ou recorrentes que têm a opção ativada?
   - O campo correspondente deve ser removido do banco de dados ou apenas ocultado?
6. **Se for a Alternativa B:**
   - O boletim sem QR Code deve ter uma marcação visível, como "apenas para conferência" ou "sem validade oficial"?
   - O layout deve ser o do novo mecanismo de geração ou o do antigo?
7. Quem usa essa opção hoje e com que frequência? Algum fluxo administrativo depende dela?
8. Existe um limite aceitável de tempo ou de carga para gerar boletins para centenas de alunos no envio de uma notificação?
9. Qual é a stack, quais são os comandos de build e teste e qual é a estrutura do repositório do Sapos? Nada disso está informado na issue.