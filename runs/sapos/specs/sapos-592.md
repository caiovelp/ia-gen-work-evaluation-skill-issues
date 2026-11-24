# Especificação: Suporte a Unicode no título de dissertação/tese (MySQL)

## Objetivo

Hoje não é possível cadastrar no SAPOS uma dissertação ou tese cujo título contenha o caractere "sigma". O MySQL rejeita o valor com o erro `Incorrect String Value`. Segundo a issue, o tipo do campo precisa mudar para aceitar Unicode.

**Usuário afetado:** quem cadastra dissertações e teses no SAPOS, como secretaria e coordenação (perfil exato não informado).

**Histórias de usuário / critérios de aceitação:**
- Como usuário que cadastra uma dissertação ou tese, quero salvar títulos com caracteres Unicode como σ, Σ, letras gregas e símbolos matemáticos, sem receber erro.
- O título salvo é exibido exatamente como foi digitado, sem `?`, mojibake ou truncamento.
- Os títulos já existentes continuam íntegros depois da alteração.

**Escopo mínimo:** o campo de título da dissertação/tese. A extensão a outros campos ou tabelas está em Questões em Aberto.

## Premissas

1. O SAPOS citado é o Sistema de Apoio à Pós-Graduação. A issue não informa versão nem stack, então a stack (por exemplo, Ruby on Rails com migrações) é uma premissa a confirmar.
2. O problema ocorre só com MySQL/MariaDB. Outros bancos suportados, como SQLite em desenvolvimento, não apresentam o erro.
3. A coluna de título usa hoje um charset sem suporte completo a Unicode: `latin1` ou `utf8`/`utf8mb3`.
   - O σ grego (U+03C3) cabe em `utf8mb3`. Se a coluna já for `utf8mb3`, o erro sugere que o caractere usado foi um símbolo matemático de 4 bytes, como 𝜎 (U+1D70E).
   - Por isso, a correção-alvo é converter para `utf8mb4`, que cobre os dois casos.
4. A conexão da aplicação com o banco também precisa usar `utf8mb4`. Alterar só a coluna pode não bastar.
5. A alteração deve preservar os dados existentes, sem perda nem conversão incorreta.
6. O comprimento máximo atual do campo deve ser mantido, respeitando os limites de índice do MySQL com `utf8mb4` caso o campo seja indexado.

## Stack Tecnológica

- Banco de dados: MySQL (versão não informada).
- Linguagem, framework e versões: Não informado na issue original.

## Comandos

Não informado na issue original.
- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Migração de banco: desconhecido

## Estrutura do Projeto

Não informado na issue original. Não se conhecem os caminhos do model de dissertação/tese, das migrações, do schema nem da configuração de banco.

## Estilo de Código

Não informado na issue original. Deve-se seguir as convenções já existentes no repositório, que não foram vistas.

## Estratégia de Testes

Os detalhes de framework, local dos testes e cobertura não foram informados na issue original. Níveis de teste esperados:
- **Integração com MySQL:**
  - Salvar e recarregar uma dissertação/tese com título contendo `σ`, `Σ`, `𝜎` (4 bytes) e acentos do português, conferindo que o valor lido é igual ao gravado.
  - Isso exige um ambiente de teste com MySQL. Não se sabe se o CI atual roda contra MySQL.
- **Migração:**
  - Aplicar a alteração numa base com títulos existentes acentuados e verificar que nada foi corrompido.
  - Verificar também se a alteração é reversível, caso o projeto use migrações reversíveis.
- **Manual:**
  - Cadastrar pela interface uma tese com sigma no título e confirmar que é salva e exibida corretamente nas telas de listagem, detalhe e eventuais relatórios ou PDFs.

## Limites

- **Sempre:**
  - Preservar os dados existentes.
  - Testar contra MySQL real.
  - Seguir o mecanismo de migração já usado pelo projeto.
- **Perguntar antes:**
  - Alterar o charset ou collation da tabela inteira ou do banco inteiro, em vez de só a coluna.
  - Alterar a configuração de conexão (encoding).
  - Mudar o tamanho ou tipo do campo, por exemplo de `VARCHAR` para `TEXT`.
  - Estender a alteração a outras colunas.
  - Adicionar dependências.
- **Nunca:**
  - Remover, sanitizar ou substituir silenciosamente os caracteres Unicode do título como "solução".
  - Executar a migração em produção sem backup.
  - Remover testes que falham sem aprovação.

## Critérios de Sucesso

- [ ] Com MySQL, é possível cadastrar e editar uma dissertação/tese com título contendo σ, Σ e símbolos de 4 bytes como 𝜎, sem o erro `Incorrect String Value`.
- [ ] O título é persistido e lido byte a byte igual ao informado.
- [ ] A exibição está correta nas telas e saídas que mostram o título.
- [ ] A coluna de título está em `utf8mb4`, com collation compatível com a usada no restante do banco.
- [ ] A conexão da aplicação com o MySQL usa `utf8mb4`.
- [ ] Os títulos existentes antes da migração permanecem inalterados.
- [ ] Há um teste automatizado ou roteiro de verificação documentado cobrindo o salvamento de título com Unicode.

## Questões em Aberto

1. Qual caractere exato causou o erro: σ (U+03C3, 2 bytes em UTF-8) ou um símbolo matemático como 𝜎 (U+1D70E, 4 bytes)? Isso indica se a coluna está em `latin1` ou `utf8mb3`.
2. Qual o charset/collation atual da coluna, da tabela e do banco em produção? Qual a versão do MySQL/MariaDB?
3. A correção deve se limitar ao título da dissertação/tese ou abranger outros campos textuais que também podem receber Unicode, como resumo, palavras-chave, nomes e títulos de disciplinas? Ou a tabela/banco inteiro?
4. O encoding da conexão com o banco já está configurado como `utf8mb4`?
5. A coluna de título está indexada? Com `utf8mb4`, índices em `VARCHAR(255)` podem exceder o limite de bytes em versões antigas do MySQL.
6. Qual o tamanho da tabela em produção? Isso afeta o tempo de bloqueio do `ALTER TABLE` e a necessidade de janela de manutenção.
7. Há outros bancos suportados, como PostgreSQL ou SQLite, em que a migração precise ser condicional ou neutra?
8. O título é usado em geração de PDFs, relatórios ou exportações que também precisem suportar esses caracteres, por exemplo com fontes que tenham os glifos?