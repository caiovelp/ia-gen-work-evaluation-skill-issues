## Resumo

Na tela de edição de uma candidatura com arquivos já enviados, o botão de salvar não responde quando existe um campo de arquivo obrigatório já preenchido. Não aparece mensagem de erro e nenhuma requisição é enviada ao servidor. O problema ocorre mesmo quando todos os campos obrigatórios estão preenchidos, por exemplo numa candidatura aprovada.

Segundo o relato, os parciais que montam os campos de arquivo marcam o input como `required` sempre que a configuração do campo o define como obrigatório, mesmo que o arquivo já esteja gravado. O navegador nunca pré-preenche inputs de arquivo, então para a validação HTML5 o campo continua vazio e o formulário inteiro é bloqueado. Quando já existe arquivo, o input fica escondido (`display: none`). Por isso o navegador não consegue focá-lo para mostrar o balão de validação, e a recusa acontece sem nenhum aviso.

**Alcance:** praticamente toda candidatura já submetida que tenha campo de arquivo obrigatório preenchido. Afeta a tela do candidato e a edição administrativa.

**Issues relacionadas, mas distintas:**
- #605: caso oposto. O formulário passa pela validação do cliente e o servidor recusa.
- #604: perda dos arquivos selecionados quando há erro de validação.

## Passos para reproduzir

1. Abra a tela de edição de uma candidatura que tenha pelo menos um campo de arquivo obrigatório com arquivo já gravado. Uma candidatura aprovada serve como exemplo. O teste pode ser feito pela tela do candidato ou pela edição administrativa.
2. Opcionalmente, altere algum outro campo do formulário.
3. Clique em salvar.
4. Observe a página e o console do navegador (Chrome).

## Comportamento observado

- Clicar em salvar não tem efeito: a página fica parada, sem mensagem de erro e sem requisição ao servidor.
- O input do campo de arquivo obrigatório já preenchido é renderizado com `required="required"` e `style="display: none"`.
- Num registro real de homologação com seis anexos, `checkValidity()` do formulário retornou `false`, com cinco campos de arquivo inválidos. Todos esses campos tinham arquivo gravado.
- O Chrome recusa o envio e registra apenas um aviso no console (ver seção abaixo).

## Comportamento esperado

O formulário deve ser submetido normalmente quando os campos de arquivo obrigatórios já têm arquivo gravado, permitindo salvar alterações em outros campos. A obrigatoriedade desses campos continua sendo verificada no servidor (`validate_file_field`), que é onde o arquivo gravado pode ser conferido.

## Stack trace / saída de erro

Mensagem registrada no console do Chrome (reproduzida de forma abreviada no relato original):

```
An invalid form control ... is not focusable
```

Atributos medidos no input renderizado:

```
input required = "required"
input style    = "display: none"
```

Resultado da validação do formulário no registro de homologação: `checkValidity() == false`, com cinco campos de arquivo inválidos.

## Caso de teste

Caso de teste mínimo, descrito a partir das medições do relato:

- **Pré-condição:** candidatura com um campo de arquivo configurado como obrigatório (`configuration["required"]` verdadeiro) e com arquivo já gravado.
- **Ação:** renderizar a tela de edição dessa candidatura.
- **Verificação:** inspecionar o input de arquivo correspondente.
  - Hoje ele sai com `required="required"` e `display: none`.
  - No navegador, `checkValidity()` do formulário retorna `false` e o envio é bloqueado.

O relato não traz código de teste.

## Exemplo de código

Trecho presente nos dois parciais que montam campo de arquivo do candidato:

```erb
options[:required] = configuration["required"] ? true : false
```

Arquivos citados:
- `app/views/admissions/filled_form/edit/_generic_file_field.html.erb`
- `app/views/admissions/filled_form/edit/_as_student_photo.html.erb`

## Versão e ambiente

- Navegador: Chrome (versão não informada).
- O problema foi observado num registro real do ambiente de homologação.
- Versão da aplicação, sistema operacional e demais detalhes: Não informado na issue original.