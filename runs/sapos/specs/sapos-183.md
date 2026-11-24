# Spec: Checagem de credenciamento ao salvar matrícula

## Objetivo

Garantir que toda matrícula salva tenha um orientador credenciado no nível do curso do aluno. Por exemplo, uma matrícula de mestrado precisa de um orientador credenciado no mestrado. Isso evita que se registrem orientações irregulares em relação às regras de credenciamento do programa.

**Usuário:** quem cadastra ou edita matrículas no sistema, como a secretaria ou a coordenação do programa (papel exato não informado).

**Regra de negócio, como descrita na issue:**
1. Ao salvar uma matrícula, verificar se **pelo menos um** dos orientadores vinculados é credenciado no nível da matrícula (ex.: mestrado).
2. Orientadores **não credenciados** no nível são permitidos na matrícula.
3. Um orientador não credenciado no nível **não pode ser o orientador principal**.

**Leitura consolidada (a confirmar):** o orientador principal precisa ser credenciado no nível da matrícula. Se essa regra for cumprida, a regra 1 também é. Os demais orientadores (coorientadores) podem ou não ser credenciados.

**Critérios de aceitação (rascunho):**
- Matrícula de nível X cujo orientador principal é credenciado em X: salvamento permitido.
- Matrícula de nível X cujo orientador principal não é credenciado em X: salvamento bloqueado, com mensagem de erro clara.
- Matrícula de nível X sem nenhum orientador credenciado em X: salvamento bloqueado, com mensagem de erro clara.
- Matrícula de nível X com orientador principal credenciado e coorientador não credenciado em X: salvamento permitido.

## Premissas

1. "Nível da matrícula" é um atributo já existente da matrícula, com valores como mestrado e doutorado.
2. O credenciamento de um orientador é registrado por nível e já existe no sistema. A issue não descreve um modelo novo de credenciamento.
3. A matrícula já tem o conceito de "orientador principal", distinto dos demais orientadores.
4. A validação vale tanto na criação quanto na edição de uma matrícula, já que a issue diz "ao salvar".
5. A validação é uma regra de backend, aplicada antes de persistir. Uma eventual validação na interface é complementar.
6. O credenciamento em um nível não implica credenciamento em outro. Por exemplo, credenciado no doutorado **não** conta automaticamente como credenciado no mestrado, a menos que isso seja confirmado.
7. Matrículas já existentes que violam a regra não são alteradas automaticamente. A regra só atua quando a matrícula é salva.

## Stack Tecnológica

Não informado na issue original.

## Comandos

Não informado na issue original.
- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Não informado na issue original. Ainda é preciso identificar onde ficam:
- a entidade/modelo de matrícula;
- o modelo de orientador e de credenciamento;
- o ponto de persistência ou validação da matrícula (formulário, serviço, model).

## Estilo de Código

Não informado na issue original. Seguir as convenções já existentes no repositório, incluindo o idioma dos identificadores e o padrão das mensagens de validação.

## Estratégia de Testes

Framework e localização dos testes: não informado na issue original.

Cobertura mínima esperada para esta regra:
- **Testes unitários da validação:**
  - principal credenciado no nível → válido;
  - principal não credenciado no nível, coorientador credenciado → inválido;
  - nenhum orientador credenciado no nível → inválido;
  - principal credenciado e coorientador não credenciado → válido;
  - principal credenciado em outro nível (ex.: doutorado numa matrícula de mestrado) → comportamento conforme a resposta às Questões em Aberto;
  - matrícula sem orientadores → comportamento conforme a resposta às Questões em Aberto.
- **Teste de integração do fluxo de salvamento:** criação e edição bloqueadas quando a regra é violada, com a mensagem de erro exibida ao usuário.

## Limites

- **Sempre:**
  - aplicar a validação no salvamento (criação e edição);
  - retornar uma mensagem de erro clara que indique o orientador e o nível;
  - cobrir com testes todos os cenários listados acima.
- **Perguntar antes:**
  - alterar o esquema de dados de matrícula, orientador ou credenciamento;
  - corrigir ou migrar matrículas já existentes que violam a regra;
  - adicionar dependências.
- **Nunca:**
  - remover ou alterar silenciosamente orientadores de uma matrícula para "fazê-la passar";
  - desabilitar a validação existente;
  - remover testes que estejam falhando sem aprovação.

## Critérios de Sucesso

- [ ] Não é possível salvar (criar ou editar) uma matrícula cujo orientador principal não seja credenciado no nível da matrícula.
- [ ] Não é possível salvar uma matrícula sem nenhum orientador credenciado no nível da matrícula.
- [ ] É possível salvar uma matrícula com coorientadores não credenciados no nível, desde que o principal seja credenciado.
- [ ] Ao bloquear, o usuário recebe uma mensagem de erro que explica o motivo.
- [ ] Todos os cenários da Estratégia de Testes têm testes automatizados passando.

## Questões em Aberto

1. **Equivalência das regras:** a regra é apenas "o orientador principal deve ser credenciado no nível"? Ou existe algum caso em que basta um coorientador credenciado, mesmo com o principal não credenciado?
2. **Hierarquia de níveis:** um orientador credenciado no doutorado é considerado credenciado para o mestrado?
3. **Validade do credenciamento:** o credenciamento tem período de vigência (data de início e fim)? A checagem deve considerar a data atual, a data de início da matrícula ou outra data?
4. **Matrícula sem orientador:** é permitido salvar uma matrícula sem orientadores, por exemplo antes da definição da orientação? Se sim, a regra só se aplica quando há orientadores?
5. **Matrículas existentes:** o que fazer com matrículas já gravadas que violam a regra? Elas devem ficar bloqueadas para qualquer edição até serem corrigidas, ou apenas exibir um aviso?
6. **Bloqueio ou aviso:** a violação deve impedir o salvamento (erro) ou apenas alertar o usuário? Algum perfil, como a coordenação, pode forçar o salvamento?
7. **Orientadores externos:** existem orientadores externos ao programa? Como o credenciamento deles é tratado?
8. **Texto da mensagem de erro:** existe um padrão ou texto específico desejado?
9. **Mudança de credenciamento:** se o credenciamento de um orientador for revogado depois, isso afeta as matrículas já salvas, ou a regra vale apenas no momento do salvamento?