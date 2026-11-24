# Spec: Campo de arquivo obrigatório já preenchido impede salvar a candidatura

## Objetivo

Corrigir a edição de candidaturas. Hoje, quando a candidatura já tem arquivos enviados, o formulário não pode ser salvo e o usuário não recebe nenhum aviso.

**Problema:** os parciais que montam campos de arquivo marcam `required` sempre que a configuração do campo diz `"required"`. Isso vale também quando já existe arquivo gravado. Os navegadores nunca pré-preenchem `<input type="file">`, então o HTML5 considera o campo vazio e bloqueia a submissão. Quando há arquivo, o input fica escondido (`display: none`). O navegador então não consegue exibir o balão de validação, e o botão de salvar parece não fazer nada. O Chrome só registra `An invalid form control ... is not focusable` no console.

**Usuários afetados:**
- O candidato, ao editar a própria candidatura.
- O administrador, ao editar uma candidatura.

**Alcance:** qualquer candidatura com campo de arquivo obrigatório já preenchido. Na prática, quase toda candidatura submetida.

**Comportamento esperado (critérios de aceitação):**
- Um campo de arquivo obrigatório **sem** arquivo gravado continua com `required` no HTML.
- Um campo de arquivo obrigatório **com** arquivo gravado é renderizado **sem** o atributo `required`.
- Numa candidatura com todos os obrigatórios preenchidos, incluindo os arquivos, salvar envia a requisição ao servidor mesmo que nenhum arquivo novo tenha sido escolhido.
- A obrigatoriedade continua sendo verificada no servidor por `validate_file_field`, contra o que está gravado.
- A correção vale para os dois parciais:
  - `app/views/admissions/filled_form/edit/_generic_file_field.html.erb`
  - `app/views/admissions/filled_form/edit/_as_student_photo.html.erb`

## Premissas

1. Os dois parciais citados são os únicos pontos que marcam `required` em campos de arquivo do candidato. A issue diz que são "os dois parciais", mas não houve busca no repositório para confirmar.
2. A tela do candidato e a edição administrativa usam esses mesmos parciais. Por isso, a correção neles cobre os dois fluxos.
3. Os parciais têm acesso a alguma informação que indica se já existe arquivo gravado para o campo, já que hoje decidem esconder o input (`display: none`) com base nisso. O nome exato dessa variável ou método não aparece na issue.
4. `validate_file_field` já impõe corretamente a obrigatoriedade no servidor quando não há arquivo gravado nem arquivo novo. Fica fora do escopo alterá-lo.
5. O stack é Ruby on Rails com views ERB, deduzido pelos caminhos e pela sintaxe. A versão é desconhecida.
6. Não haverá substituto em JavaScript para a validação de obrigatoriedade no cliente nos campos que já têm arquivo. O servidor é a fonte de verdade.

## Stack

- Ruby on Rails com templates ERB (deduzido). Versões não informadas na issue original.
- Validação de formulário HTML5 no navegador. O comportamento descrito foi observado no Chrome.

## Comandos

Não informado na issue original.
- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Servidor de desenvolvimento: desconhecido

## Estrutura do projeto

Só os caminhos citados na issue são conhecidos:

```
app/views/admissions/filled_form/edit/_generic_file_field.html.erb  → parcial de campo de arquivo genérico
app/views/admissions/filled_form/edit/_as_student_photo.html.erb    → parcial de campo de foto do candidato
```

- A localização de `validate_file_field` não é informada (provavelmente um model ou concern).
- O diretório de testes e o framework (RSpec ou Minitest) são desconhecidos.

## Estilo de código

Trecho atual, o único código mostrado na issue:

```erb
options[:required] = configuration["required"] ? true : false
```

As convenções de estilo do projeto não foram informadas na issue original. A alteração deve manter o estilo dos parciais existentes.

## Estratégia de testes

Não há framework nem convenção de testes informados na issue original. Os níveis de verificação necessários:

**Teste de view/renderização (para cada um dos dois parciais):**
- Campo obrigatório **com** arquivo gravado: o input não tem `required`. Ele continua `display: none`, mantendo o comportamento visual atual.
- Campo obrigatório **sem** arquivo gravado: o input tem `required`.
- Campo não obrigatório, com ou sem arquivo: o input não tem `required`.

**Teste de servidor (regressão):**
- `validate_file_field` continua recusando um campo obrigatório sem arquivo gravado e sem upload novo.

**Teste de sistema/navegador (se houver infraestrutura):**
- Ao editar uma candidatura com arquivos obrigatórios já enviados e alterar outro campo, o salvamento dispara a requisição e persiste a alteração.
- Na tela de edição dessa candidatura, `form.checkValidity()` retorna `true`.

**Verificação manual:**
- Repetir o cenário de homologação (registro com seis anexos). Hoje há cinco campos de arquivo inválidos. Depois da correção, `checkValidity()` deve retornar `true` e o salvamento deve funcionar.
- Fazer o mesmo pela tela do candidato e pela edição administrativa.

Requisitos de cobertura: não informado na issue original.

## Limites

**Sempre:**
- Manter a validação de obrigatoriedade no servidor (`validate_file_field`) como fonte de verdade.
- Aplicar a mesma regra nos dois parciais.
- Cobrir a tela do candidato e a edição administrativa.

**Perguntar antes:**
- Alterar `validate_file_field` ou qualquer lógica de validação no servidor.
- Adicionar JavaScript de validação no cliente.
- Mudar a visibilidade (`display: none`) ou o fluxo de substituição de arquivo.
- Adicionar dependências.

**Nunca:**
- Remover a obrigatoriedade de campos de arquivo no servidor.
- Misturar esta correção com os problemas das issues #604 (perda dos arquivos selecionados quando há erro de validação) e #605 (formulário passa no cliente e o servidor recusa).
- Remover ou desativar testes existentes sem aprovação.

## Critérios de sucesso

- [ ] Nos dois parciais, `required` só é emitido quando o campo é obrigatório **e** não há arquivo gravado.
- [ ] Na tela de edição de uma candidatura com todos os campos de arquivo obrigatórios preenchidos, `form.checkValidity()` retorna `true`.
- [ ] Clicar em salvar nessa tela envia a requisição ao servidor, tanto na tela do candidato quanto na edição administrativa.
- [ ] Alterar um campo que não é de arquivo numa candidatura aprovada e salvar persiste a alteração.
- [ ] Um campo de arquivo obrigatório sem arquivo gravado continua bloqueado no cliente (`required`) e no servidor (`validate_file_field`).
- [ ] O console do navegador não mostra mais `An invalid form control ... is not focusable` nesse fluxo.
- [ ] Há testes automatizados cobrindo a presença e a ausência de `required` nos dois parciais.

## Perguntas em aberto

1. Qual variável ou método os parciais usam hoje para saber se já existe arquivo gravado, ou seja, para decidir o `display: none`? Esse sinal é confiável nos dois parciais?
2. Existem outros parciais ou componentes com campo de arquivo e `required` incondicional que tenham o mesmo problema? Por exemplo, outros tipos de campo de arquivo além do genérico e da foto.
3. A tela do candidato e a edição administrativa usam de fato os mesmos parciais, ou há templates separados para o fluxo administrativo?
4. Se o usuário remover o arquivo gravado na tela, caso essa ação exista, o campo deve voltar a ser `required` no cliente? Isso exigiria JavaScript.
5. Quando o servidor recusa por `validate_file_field`, a mensagem de erro aparece de forma visível na tela? (Relaciona-se à #605. Confirmar se fica fora do escopo.)
6. Qual o framework de testes e quais os comandos de build, teste e lint do projeto?
7. Existe infraestrutura de testes de sistema com navegador (Capybara, Selenium ou Cuprite) para cobrir o cenário de submissão real?
8. Inputs invisíveis com validação HTML5 também devem ser evitados em outros tipos de campo do formulário? Ou o escopo se limita aos campos de arquivo?