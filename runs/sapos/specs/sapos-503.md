# Spec: Registro de Projetos Coordenados por Docentes

## Objetivo

Permitir que cada docente registre os projetos que coordena. Esses registros servirão de insumo para a autoavaliação (institucional ou do programa; ver Perguntas em Aberto).

**Usuário principal:** docente coordenador de projeto.
**Usuário secundário (presumido):** quem conduz a autoavaliação e consulta ou consolida os dados.

**Histórias de usuário:**
- Como docente, quero cadastrar um projeto que coordeno, para que ele conste na autoavaliação.
- Como docente, quero ver os projetos que já registrei, para conferir se as informações estão completas.
- Como docente, quero corrigir ou remover um projeto registrado por engano *(presumido; não consta na issue)*.

**Dados por projeto (conforme a issue):**

| Campo | Descrição | Observações |
|---|---|---|
| Título | Título do projeto | Obrigatório (presumido) |
| Ano | Ano do projeto | Significado exato a definir (início? vigência?) |
| Tipo de financiamento | Público ou privado | Valores fechados: `público`, `privado` |
| Financiador | Ex.: CNPq, FAPERJ, nome da empresa | Texto livre ou lista? A definir |
| Valor total | Valor total do projeto | Moeda e formato a definir |

## Premissas

1. A funcionalidade será adicionada a um sistema já existente que tem cadastro e autenticação de docentes. A issue fala em "cada docente", o que indica usuários identificados.
2. Cada projeto fica vinculado a um único docente coordenador, aquele que o registrou.
3. O docente gerencia apenas os seus próprios projetos.
4. "Tipo de financiamento" admite exatamente dois valores: público ou privado. Projetos sem financiamento ou com financiamento misto ficam fora do escopo até decisão contrária.
5. "Valor total" é um valor monetário em reais (BRL), com duas casas decimais.
6. "Ano" é um ano com quatro dígitos e representa o ano de início do projeto.
7. Todos os cinco campos são obrigatórios.
8. Escopo mínimo de operações: criar, listar os próprios projetos, editar e excluir.
9. Exportação e relatórios consolidados para a autoavaliação não fazem parte desta entrega. Ficam registrados como pergunta em aberto.

## Stack Tecnológica

Não informado na issue original. A linguagem, o framework, o banco de dados e as versões são desconhecidos.

## Comandos

Não informado na issue original.

- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Não informado na issue original. A localização dos modelos, das telas e dos testes no repositório é desconhecida.

## Estilo de Código

Não informado na issue original. Seguir as convenções já existentes no repositório, que precisam ser identificadas antes da implementação.

## Estratégia de Testes

O framework e os diretórios de teste não foram informados na issue original. As preocupações a cobrir, independentemente da ferramenta, são:

- **Unitários (validação):**
  - campos obrigatórios;
  - tipo de financiamento restrito a público ou privado;
  - ano válido;
  - valor total numérico e não negativo.
- **Integração (persistência e permissões):**
  - o projeto fica vinculado ao docente autenticado;
  - um docente não vê, não edita e não exclui projetos de outro docente.
- **Ponta a ponta / manual:** o docente cadastra, lista, edita e exclui um projeto pela interface.

A meta de cobertura não foi informada.

## Limites

- **Sempre:**
  - validar as entradas (campos obrigatórios, domínio do tipo de financiamento, formato de ano e valor);
  - associar o projeto ao docente autenticado;
  - rodar os testes antes de commitar;
  - seguir as convenções existentes do repositório.
- **Perguntar antes:**
  - alterar o esquema do banco de dados (nova tabela ou entidade de projeto);
  - adicionar dependências;
  - criar relatórios ou exportações;
  - permitir múltiplos coordenadores ou participantes;
  - transformar "Financiador" em lista controlada.
- **Nunca:**
  - permitir que um docente altere projetos de outro;
  - expor dados de projetos sem autenticação;
  - commitar segredos;
  - remover testes que estejam falhando sem aprovação.

## Critérios de Sucesso

1. Um docente autenticado consegue registrar um projeto com Título, Ano, Tipo de financiamento, Financiador e Valor total, e o registro fica persistido.
2. O formulário rejeita, com mensagem clara:
   - campos obrigatórios vazios;
   - tipo de financiamento diferente de público ou privado;
   - ano inválido;
   - valor total não numérico ou negativo.
3. O docente vê a lista dos projetos que registrou, com os cinco campos.
4. O docente consegue editar e excluir os próprios projetos *(presumido)*.
5. Um docente não consegue ver, editar nem excluir projetos registrados por outro docente.
6. Os dados registrados podem ser recuperados para uso na autoavaliação. O formato de consumo depende da resposta às Perguntas em Aberto.

## Perguntas em Aberto

1. **Sistema-alvo:** em qual sistema ou repositório a funcionalidade entra? Qual é a stack, quais são os comandos de build e teste e onde fica o cadastro atual de docentes?
2. **Ano:** o campo "Ano" é o ano de início, o ano de aprovação ou o ano de referência? Projetos que duram vários anos precisam de início e fim?
3. **Valor total:** a moeda é sempre BRL? Projetos com financiamento estrangeiro entram em outra moeda? O valor é o total aprovado ou o efetivamente recebido?
4. **Tipo de financiamento:** como classificar projetos sem financiamento ou com financiamento misto (público e privado)?
5. **Financiador:** o campo será texto livre ou uma lista controlada (CNPq, FAPERJ, CAPES, FINEP etc.) com opção "outro"? Um projeto pode ter mais de um financiador?
6. **Coordenação:** um projeto pode ter mais de um coordenador? Projetos em que o docente é apenas participante também devem ser registrados?
7. **Autoavaliação:**
   - quem consome esses dados (coordenação do programa, comissão de autoavaliação)?
   - essas pessoas precisam de uma visão consolidada de todos os docentes?
   - precisam de filtros (por ano, por tipo) ou de exportação (CSV, planilha)?
8. **Permissões:** algum perfil administrativo pode registrar ou editar projetos em nome de docentes?
9. **Campos adicionais:** há outros dados úteis para a autoavaliação que convém prever desde já, como número do processo, vigência, situação (em andamento ou concluído) e link?
10. **Dados históricos:** existe uma base prévia de projetos (planilha, Lattes) a importar, ou o registro começa vazio?