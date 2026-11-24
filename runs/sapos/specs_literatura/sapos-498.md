## Resumo
Adicionar um campo de observação em matrícula que seja exibido no histórico (e, possivelmente, no boletim).

## Descrição
A PROPPI pediu que se informe, em um campo de observação, quando o curso for feito na modalidade de cotutela. A partir dessa demanda, propõe-se uma solução mais genérica: um campo "Observação para o histórico" na matrícula. Quando esse campo estiver preenchido, o histórico deve mostrar uma área de observação com o texto informado.

A issue original traz uma captura de tela com um exemplo do layout. O texto em azul na imagem corresponde ao conteúdo que viria do campo "Observação para o histórico" da matrícula.

<img width="756" alt="Screenshot 2024-09-08 at 09 43 47" src="https://github.com/user-attachments/assets/40d60b18-cab1-434e-aab5-e3be8dc77c93">

A PROPPI mencionou somente o histórico. O autor da issue entende que o mesmo comportamento também deveria valer para o boletim.

## Versão do produto
Não informado na issue original.

## Justificativa
- A PROPPI precisa registrar no histórico quando o curso for feito na modalidade de cotutela.
- Uma solução genérica permite incluir quaisquer observações nos históricos, não apenas a de cotutela. Assim, ela atende a demandas futuras parecidas.

## Caso de uso ou cenário
Um aluno faz o curso na modalidade de cotutela. O usuário responsável preenche o campo "Observação para o histórico" na matrícula desse aluno com a informação sobre a cotutela. Ao emitir o histórico (e, possivelmente, o boletim), aparece uma área de observação com esse texto. Se o campo estiver vazio, a área de observação não aparece.

## Solução possível
- Criar o campo "Observação para o histórico" na matrícula.
- Quando o campo não estiver vazio, mostrar no histórico uma área de observação com o conteúdo do campo, como na figura da issue original.
- Aplicar o mesmo comportamento ao boletim.