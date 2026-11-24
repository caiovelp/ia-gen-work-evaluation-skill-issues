# Especificação: Campo "Observação para o histórico" na matrícula, exibido no histórico e no boletim

## Objetivo

A PROPPI pediu que o histórico informe, num campo de observação, quando o curso foi feito na modalidade de **cotutela**. Em vez de tratar só esse caso, a proposta é uma solução genérica:

- Adicionar à **matrícula** um campo de texto livre chamado **"Observação para o histórico"**.
- Quando o campo estiver **preenchido**, o **histórico** gerado mostra uma **área de observação** com o texto. A issue traz uma figura de referência, cujo texto em azul vem do novo campo.
- Quando o campo estiver **vazio**, o histórico não mostra a área de observação.
- O autor da issue entende que o **boletim** deve ter o mesmo comportamento, embora a PROPPI tenha falado só do histórico.

**Usuários:**
- Quem cadastra e edita matrículas, que preenche o campo.
- Quem emite histórico e boletim.
- Discentes e PROPPI, que recebem os documentos.

**Valor:** permitir observações quaisquer nos documentos acadêmicos, como a cotutela, sem nova alteração de código para cada caso.

### Histórias de usuário / critérios de aceitação

1. Como responsável pelo cadastro, quero registrar uma "Observação para o histórico" numa matrícula para que ela apareça nos documentos oficiais do discente.
2. Como emissor de documentos, quero que o histórico mostre a área de observação só quando houver texto, para que históricos sem observação continuem iguais.
3. Como emissor de documentos, quero que o boletim mostre a mesma observação, para que os dois documentos fiquem coerentes. Este item depende de confirmação; ver Perguntas em Aberto.

## Premissas

1. O sistema já tem a entidade **matrícula** e gera **histórico** e **boletim** a partir dela. Isso se deduz da issue, mas não se sabe como está implementado.
2. A observação é **por matrícula**. Um discente com mais de uma matrícula pode ter observações diferentes em cada documento.
3. O campo é **texto livre**, opcional, sem valor padrão. Matrículas já existentes ficam com o campo vazio.
4. "Vazio" inclui texto nulo, string vazia e texto só com espaços em branco. Nesses casos a área não aparece.
5. A posição e o estilo da área de observação seguem a figura anexada. O conteúdo exato da figura (posição na página, título da seção, fonte) não aparece no texto da issue.
6. O texto é exibido como está escrito, sem formatação rica (HTML ou Markdown) e com escape de caracteres especiais.
7. A cotutela é tratada só como texto escrito no campo. Não haverá campo, flag nem preenchimento automático específico para ela.
8. O campo deve poder ser preenchido e editado na mesma tela em que se cadastra e edita a matrícula.
9. Incluir o boletim faz parte do escopo, segundo a opinião do autor. Isso fica pendente de confirmação.
10. A mudança exige alterar o esquema do banco de dados para guardar o novo campo.

## Stack Tecnológica

Não informado na issue original. A linguagem, o framework, o banco de dados e a biblioteca de geração de PDF e documentos são desconhecidos.

## Comandos

Não informado na issue original. Os comandos de build, testes, lint e servidor de desenvolvimento são desconhecidos.

## Estrutura do Projeto

Não informado na issue original. A localização do modelo de matrícula, dos formulários, dos templates de histórico e boletim e dos testes é desconhecida.

## Estilo de Código

Não informado na issue original. Seguir as convenções já existentes no repositório, que não foram vistas.

## Estratégia de Testes

Não informado na issue original quanto a framework e localização dos testes. Os comportamentos que devem ser cobertos são:

- **Modelo e persistência:**
  - A matrícula salva e recupera "Observação para o histórico".
  - O campo é opcional.
  - Matrículas existentes continuam válidas sem ele.
- **Formulário:**
  - O campo aparece com o rótulo "Observação para o histórico" na criação e edição de matrícula.
  - O valor é salvo ao submeter.
- **Histórico:**
  - Com o campo preenchido, o documento contém a área de observação com o texto exato.
  - Com o campo vazio, nulo ou só com espaços, a área não aparece.
- **Boletim** (se confirmado no escopo): os mesmos dois cenários do histórico.
- **Robustez:**
  - Textos longos e com quebra de linha não quebram o layout do documento.
  - Caracteres especiais e acentos são exibidos corretamente.
  - O conteúdo passa por escape.
- **Regressão:** o histórico e o boletim de matrículas sem observação ficam iguais aos atuais.

## Limites

- **Sempre:**
  - Manter o campo opcional e retrocompatível com matrículas existentes.
  - Esconder a área de observação quando o campo estiver vazio.
  - Fazer escape do texto exibido.
  - Rodar a suíte de testes antes de commitar.
- **Perguntar antes:**
  - A migração de esquema do banco: nome da coluna, tipo e tamanho máximo.
  - Incluir o boletim no escopo.
  - Mudanças no layout do histórico além da área de observação.
  - Mostrar o campo em listagens, buscas ou exportações.
  - Adicionar dependências.
- **Nunca:**
  - Preencher automaticamente observações em matrículas existentes.
  - Mudar o conteúdo atual do histórico ou do boletim para matrículas sem observação.
  - Criar lógica específica para cotutela fora do campo genérico.
  - Commitar segredos.

## Critérios de Sucesso

1. A matrícula tem um campo opcional "Observação para o histórico", editável na interface de cadastro e edição e persistido no banco.
2. O histórico gerado para uma matrícula com o campo preenchido mostra uma área de observação com o texto do campo, como na figura da issue.
3. O histórico gerado para uma matrícula com o campo vazio, nulo ou só com espaços não mostra a área de observação e fica igual ao comportamento atual.
4. Se o boletim for confirmado no escopo, ele segue as mesmas regras dos critérios 2 e 3.
5. Uma observação de cotutela digitada no campo aparece corretamente no histórico, atendendo à demanda da PROPPI.
6. Os testes automatizados cobrem os cenários com e sem observação para cada documento afetado, e a suíte existente continua passando.

## Perguntas em Aberto

1. **Boletim:** o boletim entra nesta entrega ou fica para depois da validação com a PROPPI?
2. **Layout:** qual é a posição exata da área de observação no histórico (rodapé, após as disciplinas, antes das assinaturas)? Qual é o título da seção, por exemplo "Observação" ou "Observações"? O texto deve ser destacado (cor, negrito) no documento final, ou o azul da figura é só para ilustrar?
3. **Tamanho e formato:** existe limite de caracteres? O texto aceita quebras de linha? Deve aceitar alguma formatação?
4. **Permissões:** quais perfis podem preencher e editar o campo?
5. **Auditoria:** as alterações nesse campo precisam ser registradas, já que afetam um documento oficial?
6. **Várias observações:** basta um único campo por matrícula, ou há necessidade de várias observações?
7. **Outras saídas:** o campo deve aparecer em outros documentos, listagens ou relatórios além do histórico e do boletim?
8. **Cotutela:** a PROPPI quer um texto padrão sugerido para a cotutela, ou o conteúdo fica a critério de quem cadastra?
9. **Idioma:** existem versões do histórico ou boletim em outro idioma? Se existirem, a observação precisa de tradução ou de um campo separado?
10. **Dados existentes:** há matrículas de cotutela já cadastradas que precisam ter a observação preenchida? Isso seria feito manualmente ou em lote?