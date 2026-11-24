# Spec: Tipo de retorno configurável em campos de consolidação para avaliação de `form_condition`

## Objetivo

Hoje as condições de formulário (`form_condition`) que dependem de um **campo de consolidação** comparam o valor calculado como **string**, e não como número. Isso produz resultados errados.

**Exemplo da issue:**
- O campo de consolidação "Nota final" calcula o valor `10`.
- Existe a condição `Nota final > 6`.
- O sistema avalia `"10" > "6"`. Na comparação lexicográfica isso dá **falso**, mas o esperado é **verdadeiro**.

**Abordagem proposta na issue:**
- Adicionar ao campo de consolidação uma **configuração que indica o tipo de valor retornado**.
- O **valor padrão** dessa configuração é **numérico**, porque todas as consolidações atuais retornam números.

**Usuários afetados:**
- Quem configura formulários com campos de consolidação e condições.
- Quem preenche formulários cujo comportamento (exibição, obrigatoriedade etc.) depende dessas condições.

**Critério de sucesso em alto nível:** condições que usam campos de consolidação comparam valores de acordo com o tipo configurado, com numérico como padrão.

## Premissas

1. "Campo de consolidação" é um tipo de campo de formulário cujo valor é calculado a partir de outros campos, como uma soma ou média que gera a "Nota final".
2. `form_condition` é o mecanismo que avalia expressões sobre valores de campos, com operadores como `>`, `<`, `>=`, `<=`, `=` e `!=`.
3. O problema atinge todos os operadores de ordenação (`>`, `<`, `>=`, `<=`), não só `>`. A igualdade também pode ser afetada, por exemplo `"10.0"` comparado com `"10"`.
4. Todas as consolidações existentes retornam números. A issue afirma isso, então o padrão numérico não deve quebrar comportamento existente.
5. Consolidações já salvas, sem a nova configuração, devem ser tratadas como numéricas, seja por migração, seja por fallback na leitura.
6. Neste momento só são necessários os tipos "numérico" e "texto/string". Outros tipos (data, booleano) estão fora do escopo, salvo indicação contrária.
7. A conversão para número acontece no momento em que a condição é avaliada, usando o tipo configurado no campo de consolidação.
8. O lado direito da condição (o literal `6` no exemplo) também é tratado como número quando o campo é numérico.

## Stack Tecnológica

Não informado na issue original.

## Comandos

Não informado na issue original.
- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Não informado na issue original. Ainda não se sabe onde ficam a definição do campo de consolidação, a lógica de `form_condition` e os testes correspondentes.

## Estilo de Código

Não informado na issue original.

## Estratégia de Testes

O framework e a localização dos testes não foram informados na issue original. Os testes devem cobrir pelo menos estes níveis:

**Unitário, avaliação de `form_condition` com campo de consolidação numérico:**
- `10 > 6` → verdadeiro (caso da issue).
- `10 < 6` → falso.
- `6 >= 6` → verdadeiro e `5.5 <= 6` → verdadeiro.
- Igualdade numérica, como `10` = `10.0`, se aplicável.

**Unitário, campo de consolidação configurado como texto:**
- A comparação continua sendo feita como string.

**Unitário, valor padrão:**
- Campo de consolidação sem a configuração explícita é tratado como numérico.

**Casos de borda:**
- Valor vazio ou nulo, ou seja, consolidação ainda não calculada.
- Valor não numérico em campo configurado como numérico.
- Números negativos e decimais.
- Separador decimal (`,` vs `.`), se o sistema usar formatação localizada.

**Integração / regressão:**
- Formulários existentes com consolidações e condições continuam funcionando, agora com o resultado correto.

## Limites

**Sempre:**
- Manter numérico como padrão do tipo de retorno.
- Garantir compatibilidade com consolidações já cadastradas.
- Cobrir com testes o caso `"Nota final" > 6`.

**Perguntar antes:**
- Alterar o esquema do banco de dados ou criar migração para a nova configuração.
- Alterar a avaliação de `form_condition` para outros tipos de campo que não sejam de consolidação.
- Adicionar tipos além de numérico e texto.
- Mudar a interface de configuração do campo de consolidação além do novo seletor de tipo.

**Nunca:**
- Alterar o comportamento de comparação de campos que não são de consolidação sem aprovação.
- Remover ou enfraquecer testes existentes de `form_condition`.

## Critérios de Sucesso

1. O campo de consolidação tem uma configuração de **tipo de retorno**, com pelo menos as opções numérico e texto.
2. O valor padrão dessa configuração é **numérico** para campos novos.
3. Campos de consolidação existentes, sem a configuração salva, são tratados como **numéricos**.
4. Com "Nota final" = `10`, a condição `Nota final > 6` avalia como **verdadeira**.
5. Para campos de consolidação numéricos, os operadores `>`, `<`, `>=` e `<=` comparam valores numericamente, inclusive com decimais e negativos.
6. Para campos de consolidação configurados como texto, a comparação segue como string.
7. Valor vazio, nulo ou não convertível em campo numérico não gera erro não tratado. O comportamento esperado depende da Pergunta em Aberto 3.
8. Os testes cobrem os cenários acima e passam.

## Perguntas em Aberto

1. **Tipos suportados:** quais opções o novo campo de tipo de retorno deve oferecer? Apenas numérico e texto, ou também data, booleano etc.?
2. **Persistência e migração:** a nova configuração exige alteração de esquema ou migração dos campos existentes? Ou basta um fallback para numérico na leitura?
3. **Valores inválidos:** como avaliar uma condição quando o campo é numérico mas o valor está vazio, nulo ou não é convertível em número? A condição deve ser falsa, gerar erro ou ser ignorada?
4. **Formato numérico:** os valores calculados podem vir formatados, por exemplo `"10,5"` ou com separador de milhar? Qual regra de conversão usar?
5. **Escopo do problema:** outros tipos de campo, como campos numéricos comuns, também são comparados como string em `form_condition`? Se sim, devem ser corrigidos nesta mesma mudança?
6. **Interface:** a configuração de tipo deve aparecer na tela de edição do campo de consolidação? Em que formato (seletor, opção oculta)?
7. **Avaliação no cliente vs. servidor:** a `form_condition` é avaliada no frontend, no backend ou em ambos? A correção precisa estar consistente nos dois lados?