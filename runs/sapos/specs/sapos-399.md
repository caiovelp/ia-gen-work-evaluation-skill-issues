# Especificação: Exportação da pauta das turmas em XLSX e CSV

## Premissas

1. Já existe no sistema uma exportação da pauta da turma em PDF, e a nova funcionalidade ficará junto dela, na mesma tela ou ação.
2. A pauta exportada em XLSX/CSV terá os mesmos dados da pauta em PDF, com uma linha por aluno e colunas para os campos da pauta.
3. O usuário principal é o professor da turma, e só quem já pode exportar o PDF poderá exportar XLSX/CSV.
4. Esta especificação trata **apenas da exportação**. A importação ("lançar as infos de volta no sistema") é uma capacidade separada, que pode ser testada à parte, e está fora do escopo. Ela aparece aqui só como motivação e em Questões em Aberto.
5. O arquivo deve ser fácil de editar em planilha. Por isso, cada aluno precisa de um identificador estável (por exemplo, a matrícula), para que um futuro reimport consiga casar as linhas com os alunos.
6. O CSV usará codificação UTF-8 e um separador compatível com o Excel em português, que provavelmente é `;`, porque a vírgula é o separador decimal. Isso precisa ser confirmado.
7. Os valores numéricos, como notas, serão gravados como números no XLSX e não como texto.

## Objetivo

Permitir que o professor exporte a pauta de uma turma nos formatos **XLSX** e **CSV**, além do PDF que já existe.

**Por quê:** o PDF não é editável. O professor precisa de um arquivo de planilha para montar a própria planilha de controle (notas, frequência etc.) e, depois, lançar essas informações de volta no sistema.

**Usuário:** professor responsável pela turma.

**Histórias de usuário:**

- Como professor, quero baixar a pauta da minha turma em XLSX, para abri-la no Excel, LibreOffice ou Google Sheets e usá-la como planilha de controle.
- Como professor, quero baixar a pauta da minha turma em CSV, para usá-la em qualquer ferramenta de planilha ou script.
- Como professor, quero encontrar essas opções no mesmo lugar da exportação em PDF, para não precisar procurá-las em outra tela.

## Pilha Tecnológica

Não informado na issue original. Linguagem, framework e biblioteca de geração de XLSX são desconhecidos.

## Comandos

Não informado na issue original. Os comandos de build, teste, lint e execução local são desconhecidos.

## Estrutura do Projeto

Não informado na issue original. A localização do código da exportação em PDF da pauta é desconhecida.

## Estilo de Código

Não informado na issue original. Deve seguir o estilo já usado no módulo de exportação em PDF da pauta.

## Estratégia de Testes

Não informado na issue original quanto a framework e local dos testes. Níveis esperados:

- **Unitário:** a geração do conteúdo CSV e XLSX a partir de uma pauta de exemplo deve produzir cabeçalhos, linhas, codificação e tipos esperados.
- **Integração:** a rota ou ação de exportação deve responder com o `Content-Type` correto (`text/csv`; `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`) e com `Content-Disposition` de download.
- **Permissão:** um usuário sem acesso à turma não deve conseguir exportar em nenhum formato.
- **Paridade:** para a mesma turma, os dados do XLSX, do CSV e do PDF devem ser os mesmos (mesmos alunos e mesmos valores).

## Limites

- **Sempre:**
  - reutilizar a mesma fonte de dados e as mesmas regras de permissão da exportação em PDF;
  - incluir um identificador único do aluno em cada linha;
  - executar os testes existentes antes de concluir.
- **Perguntar antes:**
  - adicionar nova dependência, como uma biblioteca para gerar XLSX;
  - mudar a estrutura de dados da pauta;
  - mudar o comportamento ou o layout da exportação em PDF existente;
  - incluir no arquivo dados pessoais além dos que já aparecem no PDF.
- **Nunca:**
  - permitir exportar pauta de turma à qual o usuário não tem acesso;
  - implementar a importação dentro desta entrega sem uma especificação própria;
  - quebrar a exportação em PDF existente.

## Critérios de Sucesso

1. Na tela ou ação onde hoje existe a exportação em PDF, aparecem também as opções **XLSX** e **CSV**.
2. Ao escolher **XLSX**, o navegador baixa um arquivo `.xlsx` válido, que abre sem erros no Excel e no LibreOffice Calc.
3. Ao escolher **CSV**, o navegador baixa um arquivo `.csv` em UTF-8. Ao abri-lo no Excel em português, acentos e colunas aparecem corretamente.
4. Os dois arquivos têm uma linha de cabeçalho e uma linha por aluno da turma, com os mesmos alunos e valores da pauta em PDF.
5. Cada linha contém um identificador único do aluno, como a matrícula.
6. No XLSX, as colunas numéricas, como as notas, são células numéricas e não texto.
7. O nome do arquivo identifica a turma, seguindo um padrão a definir; ver Questões em Aberto.
8. Um usuário sem permissão sobre a turma recebe erro de autorização em qualquer formato.
9. A exportação em PDF continua funcionando sem alteração.

## Questões em Aberto

1. **Importação:** o "lançar as infos de volta no sistema" deve ser uma funcionalidade separada, com especificação própria? Se sim, o formato exportado agora precisa ser exatamente o formato aceito no reimport?
2. **Conteúdo da pauta:** quais colunas a pauta contém hoje (notas por avaliação, frequência, faltas, média, situação)? O XLSX/CSV deve ter exatamente essas colunas ou colunas extras/vazias para o controle do professor?
3. **Identificador do aluno:** qual campo identifica o aluno de forma única (matrícula, CPF, ID interno)? Quais dados pessoais podem aparecer no arquivo, considerando a LGPD?
4. **Separador do CSV:** `;` ou `,`? É preciso incluir BOM UTF-8 para o Excel reconhecer os acentos?
5. **Formato numérico:** as notas no CSV devem usar vírgula ou ponto como separador decimal?
6. **Nome do arquivo:** qual padrão usar (por exemplo, código da turma, disciplina, período)?
7. **Escopo dos dados:** a exportação abrange uma etapa/bimestre específico ou todas as etapas da turma?
8. **Perfis:** além do professor, outros perfis (coordenação, secretaria) devem ter acesso a essa exportação?
9. **Formatos:** é preciso entregar os dois formatos (XLSX **e** CSV) ou um só basta? A issue diz "XLSX ou CSV".
10. **XLSX:** o arquivo deve ter formatação extra, como cabeçalho congelado, larguras de coluna ou células bloqueadas, ou basta uma planilha simples?