# Spec: AGENTS.md e skills de refatoração, homologação e teste

## Objetivo

Adicionar ao repositório instruções para agentes de IA e um conjunto de skills reproduzíveis. As skills nasceram durante a atualização para o Rails 7.2 e devem servir para qualquer trabalho futuro no projeto.

**Usuários:**
- Agentes de IA que trabalham no repositório (Claude Code e outros que leem `AGENTS.md`).
- Desenvolvedores humanos que executam ou revisam esse trabalho.

**Entregáveis:**

| Artefato | Propósito |
|---|---|
| `AGENTS.md` | Convenções de trabalho, regras de atualização de dependência, pontos cegos da suíte (SQLite × MariaDB), monkey-patches sensíveis a upgrade e regras de dado sensível. Referencia a wiki em vez de duplicar o conteúdo dela. |
| `CLAUDE.md` | Importa `@AGENTS.md`. O Claude Code lê `CLAUDE.md` e não `AGENTS.md`. O import evita duplicação e funciona no Windows, ao contrário de um symlink. |
| `.claude/skills/safe-refactor/` | Medir uma mudança pela suíte local: ler o changelog, cobrir a lacuna, rodar antes, mudar, rodar depois e comparar. |
| `.claude/skills/suite-mariadb/` | Subir um MariaDB local fiel ao de produção e rodar a suíte contra ele. |
| `.claude/skills/homologacao/` | Comparar o app antes e depois em homologação (telas, PDFs, planilhas) contra o mesmo banco, com scripts de captura e comparação. |

**Requisito transversal:** as skills documentam procedimentos realmente exercitados nesta frente, incluindo as armadilhas encontradas na prática:
- versão resolvida no lockfile;
- collation materializada versus declarada;
- verificar o próprio comparador.

## Premissas

1. O projeto é uma aplicação Rails, já atualizada ou em atualização para a 7.2.
2. A suíte roda localmente com SQLite e a produção usa MariaDB. Essa diferença é a origem dos "pontos cegos".
3. Existe uma wiki do projeto com conteúdo que o `AGENTS.md` deve referenciar. A URL e as páginas não foram informadas.
4. Cada skill segue o formato de skills do Claude Code: um diretório em `.claude/skills/<nome>/` com um `SKILL.md`, e opcionalmente scripts auxiliares.
5. Os scripts de captura e comparação da skill `homologacao` são arquivos versionados dentro do diretório da skill.
6. O `CLAUDE.md` deve conter apenas o import, ou quase só isso, para não divergir do `AGENTS.md`.
7. A entrega é só documentação e scripts de apoio. Não há mudança no código da aplicação.
8. O `AGENTS.md` e as skills serão escritos em português, como a issue.

## Stack Tecnológica

- Rails 7.2, segundo a issue. A versão do Ruby não foi informada.
- Banco de produção: MariaDB, versão não informada.
- Banco da suíte local: SQLite, versão não informada.
- Agente-alvo: Claude Code, que usa `CLAUDE.md` e `.claude/skills/`.
- A linguagem e as dependências dos scripts de captura e comparação (telas, PDFs, planilhas) não foram informadas.
- O mecanismo para subir o MariaDB local (Docker ou outro) não foi informado.

## Comandos

Não informado na issue original.

Ainda são desconhecidos:
- o comando da suíte;
- o comando para subir o MariaDB local;
- os comandos dos scripts de captura e comparação.

Esses comandos precisam constar nas próprias skills.

## Estrutura do Projeto

```
AGENTS.md                         → Instruções para agentes de IA (fonte única)
CLAUDE.md                         → Importa @AGENTS.md
.claude/skills/safe-refactor/     → Skill de refatoração medida pela suíte local
.claude/skills/suite-mariadb/     → Skill de suíte contra MariaDB local
.claude/skills/homologacao/       → Skill de comparação antes/depois em homologação
                                    (+ scripts de captura e comparação, nomes desconhecidos)
```

O restante da estrutura do repositório não foi informado na issue original.

## Estilo de Código

Não informado na issue original.

Convenções implícitas na issue:
- Não duplicar conteúdo. O `AGENTS.md` referencia a wiki e o `CLAUDE.md` importa o `AGENTS.md`.
- Usar soluções portáveis para Windows, por exemplo import em vez de symlink.

## Estratégia de Testes

Esta entrega não tem código de aplicação. A verificação se resume a validar que os artefatos funcionam:

- **`CLAUDE.md`:** abrir o Claude Code no repositório, inclusive no Windows, e confirmar que o conteúdo do `AGENTS.md` é carregado pelo import.
- **Skills:** confirmar que o Claude Code reconhece as três skills em `.claude/skills/`.
- **`suite-mariadb`:** seguir o procedimento do zero em máquina limpa e confirmar que:
  - o MariaDB sobe com versão e collation iguais às de produção;
  - a suíte roda contra ele.
- **`homologacao`:** rodar os scripts de captura e comparação contra dois estados idênticos e confirmar que nenhuma diferença é reportada. Depois, contra uma diferença conhecida, confirmar que ela é detectada. Isso aplica a regra de "verificar o próprio comparador".
- **`safe-refactor`:** exercitar o procedimento em uma mudança pequena e confirmar que gera uma comparação antes/depois legível.

O framework de testes do projeto não foi informado. Também não se sabe se haverá alguma validação automatizada desses artefatos, por exemplo lint de Markdown ou CI.

## Limites

- **Sempre:**
  - manter o `AGENTS.md` como fonte única e referenciar a wiki em vez de copiar;
  - registrar nas skills as armadilhas observadas na prática;
  - manter os procedimentos reproduzíveis, com passos e comandos explícitos.
- **Perguntar antes:**
  - adicionar dependências para os scripts de captura e comparação;
  - alterar configuração de CI;
  - mudar a configuração de banco da suíte, por exemplo o `database.yml`.
- **Nunca:**
  - incluir dado sensível, credenciais, dumps ou capturas de homologação com dados reais nos arquivos versionados;
  - usar symlink entre `CLAUDE.md` e `AGENTS.md`;
  - duplicar conteúdo da wiki.

## Critérios de Sucesso

- [ ] O `AGENTS.md` existe na raiz e cobre os cinco tópicos:
  - convenções de trabalho;
  - regras de atualização de dependência;
  - pontos cegos SQLite × MariaDB;
  - monkey-patches sensíveis a upgrade, cada um identificado;
  - regras de dado sensível.
- [ ] O `AGENTS.md` aponta para a wiki nos pontos onde ela já é a fonte, sem duplicar o conteúdo.
- [ ] O `CLAUDE.md` existe na raiz, contém `@AGENTS.md` e o Claude Code carrega o conteúdo em Linux e Windows.
- [ ] A skill `safe-refactor` descreve, na ordem, as etapas: ler o changelog, cobrir a lacuna, rodar antes, mudar, rodar depois e comparar. Também menciona a armadilha da versão resolvida no lockfile.
- [ ] A skill `suite-mariadb` permite subir um MariaDB local com a mesma versão e collation de produção e rodar a suíte contra ele. Também alerta sobre collation materializada versus declarada.
- [ ] A skill `homologacao` inclui os scripts de captura e comparação para telas, PDFs e planilhas, usando o mesmo banco nos dois estados. Também orienta a verificar o próprio comparador.
- [ ] Nenhum arquivo adicionado contém dado sensível.

## Perguntas em Aberto

1. Qual é a URL da wiki e quais páginas o `AGENTS.md` deve referenciar?
2. Quais são as versões exatas de MariaDB, Ruby e SQLite, e qual é a collation de produção?
3. Como o MariaDB local deve ser provisionado: Docker, docker-compose, instalação nativa ou outro?
4. Em que linguagem serão os scripts de captura e comparação, e quais ferramentas usam (navegador headless, diff de PDF, leitura de planilhas)? Exigem dependências novas?
5. Que banco de homologação os scripts usam, e como se obtém acesso sem expor dado sensível?
6. Quais são os monkey-patches sensíveis a upgrade a listar, e onde ficam no código?
7. Quais são as regras de dado sensível vigentes: o que não pode ir para logs, prompts, capturas ou commits?
8. Além do Claude Code, outros agentes devem ser considerados? Isso pode exigir adaptar o formato do `AGENTS.md`.
9. As skills devem ter algum metadado obrigatório, como `name`, `description` ou gatilhos de uso, seguindo um padrão interno?
10. A entrega deve ser um único PR ou ser dividida? `AGENTS.md`/`CLAUDE.md` e cada skill são entregáveis independentes que poderiam ser revisados separadamente.
11. As capturas geradas pela skill `homologacao` devem ficar fora do versionamento, por exemplo via `.gitignore`?