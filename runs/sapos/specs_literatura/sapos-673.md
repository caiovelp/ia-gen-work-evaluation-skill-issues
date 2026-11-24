## Resumo

A marca d'água dos documentos em PDF não fica centralizada no papel. Ela é carimbada em uma coordenada fixa (`pdf.stamp_at "watermark", [80, 0]` em `app/helpers/pdf_helper.rb`). O texto é desenhado em `at: [0, 0]` dentro de uma rotação em torno da origem. Nem a frase nem o papel são medidos, então a posição não pode ficar centralizada por construção.

O problema afeta todo documento com marca d'água, pois boletim, histórico e declaração compartilham o mesmo helper. Origem: #121.

## Passos para reproduzir

1. Gere um documento com marca d'água (boletim, histórico ou declaração) em papel A4 retrato.
2. Compare a posição da tinta da marca d'água com o centro da página.
3. Gere o mesmo tipo de documento em duas variantes, uma sem assinatura e outra com assinatura manual. Compare a posição da marca d'água entre elas.
4. Altere ou traduza o texto de `pdf_content.watermark` para uma frase de outro comprimento, gere o documento novamente e compare a posição da marca d'água.
5. Gere um documento com marca d'água em papel paisagem. Hoje nenhum documento com marca d'água usa paisagem.

## Comportamento observado

- **A4 retrato:** a tinta fica cerca de 35 pt à esquerda e cerca de 92 pt abaixo do centro da página.
- **Margem inferior:** a posição depende da margem inferior, que cresce para caber o rodapé de assinatura. A diferença medida entre um documento sem assinatura e um com assinatura manual é de 69,65 pt.
- **Comprimento da frase:** a fonte é monoespaçada, então editar ou traduzir `pdf_content.watermark` desloca a marca inteira.
- **Papel paisagem:** a tinta é cortada pela borda do papel.

## Comportamento esperado

A marca d'água deve ficar centralizada no papel em todo documento que a utiliza. A posição não deve variar com a margem inferior (com ou sem rodapé de assinatura), com o comprimento da frase nem com a orientação do papel, e a marca não deve ser cortada pela borda.

## Stack trace / saída de erro

Não informado na issue original.

## Caso de teste

Não informado na issue original. Os critérios de verificação que se podem extrair das medições relatadas são:

- Em A4 retrato, o centro da tinta da marca d'água deve coincidir com o centro da página. Hoje o desvio é de ~35 pt horizontalmente e ~92 pt verticalmente.
- Documentos sem assinatura e com assinatura manual devem ter a marca d'água na mesma posição. Hoje a diferença é de 69,65 pt.
- Frases de comprimentos diferentes em `pdf_content.watermark` devem permanecer centralizadas.
- Em papel paisagem, a marca d'água não deve ser cortada pela borda.

## Exemplo de código

Trechos citados na issue, em `app/helpers/pdf_helper.rb`:

```ruby
pdf.stamp_at "watermark", [80, 0]
```

O texto é desenhado com `at: [0, 0]` dentro de uma rotação em torno da origem. O código completo do helper não foi fornecido.

## Versão e ambiente

Não informado na issue original.