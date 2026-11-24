# Spec: Registro de artigos 4N para avaliação quadrienal

## Objetivo

A issue tem apenas o título: "Registro de artigos 4N para avaliação quadrienal". Não há descrição, critérios de aceite, telas, modelo de dados nem referência ao sistema existente.

Pela leitura do título, o objetivo seria **permitir registrar e consultar o conjunto de artigos "4N" que o programa indicará na avaliação quadrienal**. Isso ainda precisa ser confirmado (ver Premissas e Perguntas em Aberto).

**Usuários prováveis (a confirmar):**
- Coordenação do programa de pós-graduação, que consolida e envia a indicação.
- Docentes permanentes, que indicam ou validam seus próprios artigos.
- Secretaria do programa, que dá apoio operacional ao registro.

**Histórias de usuário candidatas (a validar):**
- Como docente permanente, quero indicar meus artigos para compor o conjunto 4N, para que minha produção seja considerada na avaliação quadrienal.
- Como coordenador, quero visualizar e consolidar os artigos indicados por todos os docentes, para que o programa respeite o limite 4N.
- Como coordenador, quero exportar a lista consolidada, para registrá-la na plataforma oficial de avaliação.

**Como seria o sucesso:** o programa consegue montar, validar e exportar a lista de artigos 4N do quadriênio sem planilhas paralelas, respeitando as regras de quantidade e elegibilidade.

## Premissas

1. "Avaliação quadrienal" refere-se à Avaliação Quadrienal da CAPES dos programas de pós-graduação stricto sensu.
2. "4N" significa um limite de artigos igual a 4 × N, em que N é o número de docentes permanentes do programa. A interpretação alternativa seria "4 artigos por docente", e a regra exata pode variar por área de avaliação.
3. O sistema que receberá a funcionalidade já possui cadastro de docentes, de programas e de produção bibliográfica (artigos).
4. O quadriênio considerado é o vigente ou o próximo. O período exato não foi informado.
5. O registro é interno ao sistema. Não há integração automática com a Plataforma Sucupira; a saída seria uma lista ou exportação para lançamento manual.
6. Só entram artigos publicados dentro do período do quadriênio e vinculados a docentes do programa.
7. Uma mesma produção, quando tem coautoria entre docentes do programa, deve contar uma única vez no total 4N.

→ Todas as premissas acima precisam de confirmação. Nenhuma vem explicitamente da issue.

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

Não informado na issue original. Framework, local dos testes e meta de cobertura são desconhecidos.

Independentemente da ferramenta, os testes deveriam cobrir estes pontos:
- **Regras de negócio (unitários):** cálculo do limite 4N a partir de N, elegibilidade por período, deduplicação de coautorias e bloqueio ao exceder o limite.
- **Persistência e permissões (integração):** quem pode indicar, editar e consolidar.
- **Exportação:** formato e conteúdo da lista final.

## Limites

- **Sempre:** validar o limite 4N e a elegibilidade antes de salvar; registrar quem indicou ou alterou cada artigo e quando; seguir as convenções existentes do projeto (desconhecidas).
- **Perguntar antes:** alterações de esquema de banco de dados; novas dependências; qualquer integração com sistemas externos (Sucupira, Lattes, ORCID); mudanças em regras de permissão existentes.
- **Nunca:** alterar ou apagar dados de produção bibliográfica já cadastrados como efeito colateral do registro 4N; expor dados de um programa a usuários de outro programa.

## Critérios de Sucesso

Os critérios abaixo são provisórios e dependem das respostas às Perguntas em Aberto:

- [ ] É possível marcar um artigo existente como integrante do conjunto 4N de um programa em um quadriênio.
- [ ] O sistema calcula e exibe o limite (4 × N) com base nos docentes permanentes do programa no quadriênio.
- [ ] O sistema impede, ou sinaliza claramente, a inclusão além do limite.
- [ ] Artigos fora do período do quadriênio, ou sem vínculo com docente do programa, não podem ser incluídos.
- [ ] Um artigo com vários docentes coautores conta uma única vez no total.
- [ ] Somente perfis autorizados (a definir) podem incluir, remover ou consolidar artigos.
- [ ] A lista consolidada pode ser visualizada e exportada (formato a definir).
- [ ] Toda inclusão ou remoção fica registrada com usuário e data.

## Perguntas em Aberto

1. **Definição de 4N:** é 4 × número de docentes permanentes, 4 artigos por docente, ou outra regra da área de avaliação? Qual é a fonte oficial (documento de área ou ficha de avaliação)?
2. **N:** como N é calculado? Considera docentes permanentes em algum momento específico, a média do quadriênio, ou docentes em qualquer ano do período?
3. **Quadriênio:** qual período (por exemplo, 2025–2028)? O sistema deve suportar vários quadriênios?
4. **Elegibilidade:** artigos precisam ter discentes ou egressos coautores, um estrato Qualis mínimo, ou vínculo com linhas ou projetos do programa?
5. **Fluxo:** o docente indica e o coordenador aprova, ou o coordenador registra tudo diretamente? Existe prazo ou bloqueio após a "consolidação"?
6. **Limite por docente:** há um máximo de artigos por docente dentro do total 4N?
7. **Coautoria:** como contabilizar artigos com vários docentes do programa? A quem o artigo é atribuído?
8. **Origem dos artigos:** os artigos já existem no sistema? Vêm do Lattes, do ORCID ou de cadastro manual? Pode-se registrar um artigo que ainda não está cadastrado?
9. **Saída:** qual formato de exportação (CSV, XLSX, PDF)? Precisa seguir o layout da Plataforma Sucupira?
10. **Perfis e permissões:** quais papéis existem hoje no sistema, e quais podem ver ou editar o registro 4N?
11. **Ordenação e justificativa:** os artigos precisam ser ranqueados ou acompanhados de texto justificando a relevância?
12. **Sistema-alvo:** em qual aplicação, módulo e stack isso será implementado? Quais são os comandos de build e teste e a estrutura do repositório?