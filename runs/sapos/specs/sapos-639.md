# Spec: Atualização da versão do Ruby (saída da série 3.2, em fim de vida)

## Premissas

1. A versão atual do projeto é **Ruby 3.2.11**, declarada em `.ruby-version`. É o último release da série 3.2, que chegou ao fim de vida em 01/04/2026.
2. A tabela de status das séries foi consultada em **24/07/2026**. Hoje é **23/11/2026**, então ela pode estar desatualizada e precisa ser reconferida antes da decisão. O vencimento da 3.3 está agora a cerca de 4 meses.
3. Segundo a política de manutenção citada na issue, a janela de correções de segurança do **Rails 7.2 já fechou** (agosto de 2026). A nota da issue de que "a janela fecha em agosto de 2026" agora descreve algo que já aconteceu. Isso reforça a pergunta sobre encadear os saltos de Ruby e de Rails.
4. Na falta de decisão do mantenedor, o alvo provisório é a **série 3.4, no patch mais recente disponível**. É a opção "conservadora" indicada na issue.
5. Esta spec cobre **só o salto de Ruby**. Ela não cobre o salto de Rails, porque não há issue aberta para ele. Se o mantenedor decidir tratar os dois juntos, esta spec deve ser revista ou decomposta.
6. O CI usa a action `setup-ruby` e lê a versão de `.ruby-version`. Por isso ele acompanha a mudança sem alteração adicional. Presume-se que a action seja do GitHub Actions, mas a issue não diz isso explicitamente.
7. O `brakeman` já roda no projeto e hoje emite um aviso de severidade alta sobre `.ruby-version`.
8. A instalação do Ruby no servidor de produção é feita fora do repositório. Quem faz e como faz não foi informado.
9. Não se sabe se o `Gemfile` declara a versão do Ruby (diretiva `ruby`) nem se o `Gemfile.lock` registra `RUBY VERSION`. A spec trata os dois como pontos a verificar.

## Objetivo

Tirar o SAPOS de uma série de Ruby em fim de vida (3.2) e levá-lo a uma série que ainda recebe correções. Hoje a 3.2 não recebe nem correção de segurança.

**Usuários afetados:**
- Mantenedores, que precisam de uma base com suporte.
- Operação do servidor de produção, que instala a nova série.
- Usuários finais, que não devem perceber mudança nos relatórios PDF e planilhas XLSX.

**Por quê:**
- Exposição a vulnerabilidades sem correção.
- O aviso de severidade alta do `brakeman`.
- A 3.3 venceria em pouco tempo, então mirar nela compraria pouco tempo.

**Fora do escopo, salvo decisão em contrário:**
- Atualização do Rails 7.2.
- Criação dos testes de caracterização de PDF/XLSX (#636). Esse é um item relacionado e recomendado, tratado em issue própria.

## Stack tecnológica

| Item | Versão | Observação |
|---|---|---|
| Ruby atual | 3.2.11 | Série 3.2, EOL desde 01/04/2026 |
| Ruby alvo | 3.4.x (provisório) ou 4.0.x | Decisão pendente do mantenedor |
| Rails | 7.2 | Compatibilidade com a série alvo a verificar; janela de segurança encerrada em ago/2026 |
| Gems com extensão nativa | `mysql2`, `sqlite3`, `nokogiri`, `bigdecimal`, `prawn`/`ttfunk` | Compilação na série alvo a verificar; versões atuais não informadas |
| Análise estática | `brakeman` | Versão não informada |
| CI | `setup-ruby` | Lê `.ruby-version` |

Os bancos de dados (MySQL e/ou SQLite, conforme as gems listadas) não têm o uso informado por ambiente.

## Comandos

Não informado na issue original.

- Build, teste, lint, dev: desconhecidos.
- Invocação do `brakeman`: a issue só diz que ele "passou a rodar no projeto". O comando e o local (CI ou local) são desconhecidos.

## Estrutura do projeto

Só os caminhos citados na issue:

```
.ruby-version          → Versão do Ruby; lida pelo setup-ruby no CI e sinalizada pelo brakeman
config/initializers/   → Monkey-patches; primeiros suspeitos em qualquer salto (conforme AGENTS.md)
AGENTS.md              → Orientações do projeto para agentes/contribuidores
```

A localização do workflow de CI, do `Gemfile`/`Gemfile.lock`, dos testes e dos geradores de PDF/XLSX é desconhecida.

## Estilo de código

Não informado na issue original.

O `AGENTS.md` existe e deve ser consultado para convenções. Seu conteúdo não foi fornecido, exceto a orientação sobre os monkey-patches em `config/initializers/`.

## Estratégia de testes

O framework de testes e a cobertura não foram informados.

**O que a issue informa:**
- A suíte existente roda no CI, que passará a usar a nova versão de Ruby automaticamente via `.ruby-version`.
- Para PDF/XLSX, a suíte só confere o **nome do arquivo**. Não há teste de caracterização do conteúdo (#636).

**Consequências para a homologação do salto:**
- Uma suíte verde é condição necessária, mas não suficiente.
- Se o #636 não estiver resolvido antes, a equivalência de relatórios e planilhas depende de **homologação manual**. Ela deve comparar saídas geradas na 3.2.11 e na série alvo a partir dos mesmos dados.
- Os monkey-patches em `config/initializers/` precisam de verificação explícita na série alvo. Isso vale principalmente para os que alteram classes do Ruby, do Rails ou das gems com extensão nativa. Não se sabe se eles têm cobertura de teste.
- O `brakeman` deve rodar após a mudança para confirmar que o aviso de EOL sumiu e que nenhum aviso novo apareceu.

## Limites

**Sempre:**
- Fixar o **patch mais recente** da série escolhida em `.ruby-version`.
- Rodar a suíte completa e o `brakeman` na série alvo antes do merge.
- Revisar `config/initializers/` conforme o `AGENTS.md`.
- Registrar no PR a evidência de homologação de PDF/XLSX.

**Perguntar antes:**
- Escolher a série alvo (3.4 ou 4.0).
- Atualizar qualquer gem além do mínimo necessário para compilar ou rodar na série alvo.
- Alterar ou remover monkey-patches.
- Mudar a ordem em relação ao salto de Rails.
- Alterar workflow de CI ou dependências de sistema.
- Fazer o deploy em produção, que depende da instalação prévia da série no servidor.

**Nunca:**
- Fazer deploy de código que exija a nova série antes que ela esteja instalada no servidor de produção.
- Desabilitar ou silenciar o aviso do `brakeman` em vez de resolver a causa.
- Remover ou afrouxar testes para fazer a suíte passar.
- Atualizar o Rails dentro desta mudança sem decisão explícita do mantenedor.

## Critérios de sucesso

- [ ] `.ruby-version` aponta para o patch mais recente da série escolhida (3.4.x ou 4.0.x). A série está em manutenção normal na data do merge, reconferida na página de branches do ruby-lang.
- [ ] Se o `Gemfile` ou o `Gemfile.lock` registram a versão do Ruby, eles estão consistentes com `.ruby-version`.
- [ ] `bundle install` conclui na série alvo, com `mysql2`, `sqlite3`, `nokogiri`, `bigdecimal` e `prawn`/`ttfunk` compilando ou instalando sem erro.
- [ ] O Rails 7.2 está confirmado como compatível com a série alvo. A fonte foi registrada no PR.
- [ ] A suíte de testes passa no CI com a nova versão, e o CI efetivamente usou a versão nova (versão do Ruby visível no log).
- [ ] Nenhum novo aviso de depreciação do Ruby aparece no log de testes, ou os que aparecem estão listados no PR com plano de tratamento.
- [ ] Cada arquivo em `config/initializers/` foi revisado. Os monkey-patches foram validados na série alvo, com o resultado registrado no PR.
- [ ] O `brakeman` não emite mais o aviso de severidade alta sobre `.ruby-version` e não introduz avisos novos.
- [ ] Há evidência de que os relatórios PDF e as planilhas XLSX gerados na série alvo são equivalentes aos da 3.2.11 para o mesmo conjunto de dados. A evidência vem de testes de caracterização (#636) ou de homologação manual documentada.
- [ ] A série alvo está instalada no servidor de produção **antes** do deploy, e a aplicação sobe e funciona em produção após o deploy.

## Perguntas em aberto

1. **Série alvo:** 3.4 (conservadora, em manutenção normal) ou 4.0? Se for 4.0, quais gems precisam ser verificadas além do Rails?
2. **Ordem em relação ao Rails:** o salto de Ruby vem antes, depois ou junto do salto de Rails? A janela de segurança do Rails 7.2 já fechou em agosto de 2026, então ele também está sem correções hoje. Isso torna o salto de Rails tão urgente quanto o de Ruby? Ele deve ganhar issue própria?
3. **Decomposição:** se os dois saltos forem tratados juntos, eles formam capacidades testáveis independentemente. Convém então um mapa com dois módulos e ordem de build, em vez de uma spec única.
4. **Servidor de produção:** a distribuição empacota a série alvo ou é preciso instalar de outra forma (gerenciador de versões, compilação)? Quem executa a instalação e com que antecedência?
5. **Testes de caracterização (#636):** o #636 deve ser resolvido antes deste salto, para servir de rede de segurança, ou a homologação manual é aceita como evidência?
6. **Homologação manual:** quais relatórios e planilhas fazem parte da amostra mínima, com quais dados, e quem aprova?
7. **Status das séries:** a tabela foi consultada em 24/07/2026. É preciso reconfirmar o status da 3.4 e da 4.0 e ver se surgiu uma série nova até a data da decisão.
8. **Gemfile/Gemfile.lock:** o projeto declara a versão do Ruby fora de `.ruby-version`? Se sim, onde?
9. **Comandos:** quais são os comandos exatos de teste, lint e `brakeman` usados localmente e no CI?
10. **Política de atualização de gems:** é aceitável atualizar gems com extensão nativa, se necessário, dentro deste mesmo PR? Ou isso deve ir num passo separado?