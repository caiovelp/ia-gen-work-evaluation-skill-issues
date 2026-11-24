# Spec: Combo de ano de trancamento limitada aos 5 anos anteriores ao ano atual

## Objetivo

Corrigir as telas que permitem editar um trancamento. Hoje a combo de seleção de ano só oferece os 5 anos anteriores ao ano atual. Isso causa dois problemas:

1. **Cadastro e edição com anos antigos:** o usuário não consegue escolher um ano de trancamento anterior a esse intervalo.
2. **Edição de trancamento existente:** se o ano já cadastrado estiver fora do intervalo, a combo aparece em branco. O usuário não consegue reselecionar o ano original. Isso pode levar à perda ou alteração indevida do dado ao salvar.

**Usuário:** quem tem acesso às telas de cadastro e edição de trancamento. O perfil exato não foi informado.

**Sucesso:** ao abrir qualquer tela de edição de trancamento, a combo de ano exibe pré-selecionado o ano já cadastrado, qualquer que seja ele. A combo também permite escolher anos anteriores ao limite atual de 5 anos, dentro de um intervalo a ser definido (ver Questões em Aberto).

### Critérios de aceitação (histórias de usuário)

- **Exibição do ano cadastrado:** Dado um trancamento existente com ano anterior a (ano atual − 5), quando o usuário abre a tela de edição, a combo exibe esse ano selecionado, e não fica em branco.
- **Salvar sem alterar o ano:** Dado o cenário acima, quando o usuário salva sem mexer no ano, o ano persistido continua igual ao original.
- **Escolher anos antigos:** Dada uma tela de edição ou cadastro de trancamento, quando o usuário abre a combo, ela oferece anos anteriores a (ano atual − 5), até o limite inferior definido.
- **Abrangência:** O comportamento é o mesmo em todas as telas onde o trancamento pode ser editado.

## Premissas

1. "Trancamento" é o trancamento de matrícula ou de curso em um sistema acadêmico, e o "ano de trancamento" é um campo persistido no registro.
2. Existe mais de uma tela que edita trancamento ("Telas", no plural), e todas têm a mesma limitação. Provavelmente usam uma lógica ou componente comum para gerar a lista de anos, mas isso não foi confirmado.
3. O limite de 5 anos é gerado dinamicamente a partir do ano atual, e não vem de uma lista fixa.
4. A combo hoje também inclui o ano atual e não inclui anos futuros. O comportamento para anos futuros deve continuar como está.
5. Os registros antigos não estão inconsistentes no banco. O problema está só na apresentação e seleção na interface.
6. Não há regra de negócio documentada que exija o limite de 5 anos. O pedido trata o limite como defeito, não como regra a ser preservada.
7. Corrigir somente a exibição do ano já cadastrado não basta: a issue pede também a possibilidade de escolher anos anteriores.

## Stack Tecnológica

Não informado na issue original.

## Comandos

Não informado na issue original.

- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Não informado na issue original. Não se sabe quais arquivos ou telas implementam a edição de trancamento, nem onde fica a lógica que gera a lista de anos.

## Estilo de Código

Não informado na issue original. Seguir as convenções já existentes no repositório, a serem verificadas.

## Estratégia de Testes

Não há framework, local ou cobertura informados na issue original. Os cenários que devem ser cobertos, no nível adequado ao projeto, são:

- **Unitário (geração da lista de anos):**
  - a lista inclui anos anteriores a (ano atual − 5), até o limite inferior definido;
  - a lista sempre inclui o ano já cadastrado, mesmo que esteja fora do intervalo padrão.
- **Integração ou tela (edição):**
  - abrir a edição de um trancamento com ano antigo (por exemplo, ano atual − 10) exibe o ano selecionado;
  - salvar sem alteração preserva o ano.
- **Regressão:**
  - trancamentos com ano dentro dos últimos 5 anos continuam funcionando como hoje;
  - o cadastro de um novo trancamento continua funcionando.
- **Abrangência:** os cenários acima devem ser verificados em cada uma das telas que editam trancamento.

## Limites

- **Sempre:**
  - garantir que o ano já cadastrado apareça selecionado na edição;
  - aplicar a correção de forma consistente em todas as telas afetadas;
  - rodar os testes existentes antes de concluir.
- **Perguntar antes:**
  - alterar o esquema do banco ou dados existentes;
  - definir o limite inferior de anos;
  - permitir anos futuros;
  - alterar regras de validação no backend;
  - adicionar dependências.
- **Nunca:**
  - alterar silenciosamente o ano de trancamentos existentes;
  - remover validações sem aprovação;
  - remover ou desativar testes que estejam falhando sem aprovação.

## Critérios de Sucesso

- [ ] Em todas as telas de edição de trancamento, um registro com ano anterior a (ano atual − 5) abre com o ano corretamente selecionado na combo.
- [ ] Salvar um trancamento antigo sem alterar o ano mantém o ano original no registro.
- [ ] A combo permite escolher anos anteriores a (ano atual − 5), até o limite inferior acordado.
- [ ] Trancamentos com ano dentro dos últimos 5 anos e cadastros novos continuam funcionando sem regressão.
- [ ] Testes automatizados cobrem os cenários acima, se houver infraestrutura de testes.

## Questões em Aberto

1. **Telas afetadas:** quais são exatamente as telas onde é possível editar o trancamento?
2. **Limite inferior:** até qual ano a combo deve ir? As opções incluem:
   - um ano fixo, como o ano de início do sistema ou da instituição;
   - um número maior de anos, como 20 ou 50;
   - o ano de ingresso do aluno ou o ano do vínculo;
   - um valor configurável.
3. **Origem dos 5 anos:** o limite foi uma escolha arbitrária ou atende a alguma regra de negócio, como prazo regimental de trancamento? Se for regra, ela vale só para novos cadastros e deve ser relaxada apenas na edição?
4. **Anos futuros:** a combo deve permitir anos futuros?
5. **Validação no backend:** existe validação no servidor que também restringe o ano a 5 anos? Ela precisa ser ajustada?
6. **Período ou semestre:** a combo de período, se existir, tem limitação semelhante que também deva ser corrigida?
7. **Dados já afetados:** algum trancamento já teve o ano perdido ou alterado indevidamente por ter sido salvo com a combo em branco? É preciso levantar e corrigir esses dados?
8. **Stack e estrutura:** qual a stack, quais os comandos de build e teste, e qual a estrutura do projeto? Nada disso consta na issue.