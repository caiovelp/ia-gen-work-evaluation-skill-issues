# Especificação: Visualização do Momento da Inscrição no SAPOS

## Objetivo

Permitir que usuários da interface do SAPOS vejam **quando** cada inscrição foi feita (data e hora). O problema relatado é que hoje é difícil identificar, por exemplo, quais estudantes se inscreveram no **período de ajustes**.

**Usuário:** quem acompanha as inscrições (coordenação ou secretaria do programa). O perfil exato não foi informado.

**Histórias de usuário:**
- Como responsável pelas inscrições, quero ver a data e a hora de cada inscrição, para saber quando o estudante se inscreveu.
- Como responsável pelas inscrições, quero identificar quais inscrições ocorreram no período de ajustes, para tratá-las de forma diferenciada.

**Critérios de aceitação preliminares (a validar):**
- A listagem e/ou o detalhe de uma inscrição mostra a data e a hora em que ela foi realizada.
- O usuário consegue distinguir as inscrições feitas no período de ajustes das feitas no período regular. Pode ser por filtro, ordenação ou indicação visual; a forma depende das Perguntas em Aberto.

### Premissas
1. "Inscrição" refere-se à inscrição de estudantes em disciplinas ou turmas, e não a processos seletivos ou matrículas no programa.
2. O "momento da inscrição" é a data e a hora em que o registro foi criado, e não a data da última alteração.
3. O sistema já guarda algum registro temporal da criação da inscrição. Isso não foi confirmado, pois o código não estava disponível.
4. O "período de ajustes" é uma janela de datas que existe no sistema ou que pode ser definida. Não se sabe se o SAPOS já modela esse período.
5. A funcionalidade é apenas de consulta. Ela não altera regras de inscrição.
6. Inscrições antigas sem registro de data confiável aparecem como "data desconhecida" e não recebem uma data inventada.

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
Não informado na issue original. Diretrizes gerais, sem ferramentas definidas:
- Testes que verificam a exibição da data e hora da inscrição na tela correspondente.
- Testes que verificam a identificação de inscrições dentro e fora do período de ajustes, incluindo os casos-limite no início e no fim da janela.
- Testes para inscrições sem data registrada.

## Limites
- **Sempre:** exibir data e hora no fuso horário da instituição, de forma consistente; manter as permissões de acesso existentes às inscrições; rodar os testes antes de cada commit.
- **Perguntar antes:** alterar o esquema do banco de dados (por exemplo, adicionar campo de data ou modelar o período de ajustes); preencher retroativamente dados de inscrições antigas; adicionar dependências; mudar regras de inscrição.
- **Nunca:** inventar ou estimar datas de inscrições antigas sem aprovação; expor essa informação a perfis que hoje não acessam as inscrições; remover testes que estejam falhando sem aprovação.

## Critérios de Sucesso
- Para toda inscrição com registro temporal, a interface mostra a data e a hora exatas em que foi feita.
- O usuário consegue obter a lista de estudantes que se inscreveram no período de ajustes de um semestre sem consultar o banco diretamente.
- Inscrições sem registro temporal aparecem de forma explícita como "data desconhecida" e não quebram a tela.
- As telas e permissões existentes continuam funcionando, sem regressões nos testes.

## Perguntas em Aberto
1. A que tipo de inscrição a issue se refere: disciplinas ou turmas, processos seletivos ou outro?
2. Em quais telas a informação deve aparecer: listagem de inscrições, detalhe do estudante, detalhe da turma, relatórios ou exportações?
3. Basta exibir data e hora em uma coluna, ou também é preciso filtrar e ordenar por data?
4. O SAPOS já registra o momento de criação das inscrições? Se sim, desde quando? Como tratar as inscrições anteriores a isso?
5. O "período de ajustes" já existe no sistema, com datas configuradas por semestre? Ou ele precisa ser modelado ou informado manualmente?
6. A interface deve destacar automaticamente as inscrições feitas no período de ajustes, por exemplo com um rótulo ou filtro, ou o usuário filtra por intervalo de datas?
7. Se uma inscrição for alterada ou cancelada e refeita, qual momento vale: o da primeira inscrição ou o da última?
8. Quais perfis de usuário podem ver essa informação?
9. Qual fuso horário e formato de data e hora usar na exibição?