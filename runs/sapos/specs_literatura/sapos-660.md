## Resumo

Na listagem de Turmas do SAPOS, os links de paginação no rodapé da tela não respeitam o filtro atual. Ao trocar o filtro de professor pelo filtro de PERÍODO, a página 1 mostra o resultado correto. Ao clicar na página 2, porém, o sistema volta a aplicar o filtro anterior (professor).

## Passos para reproduzir

1. Acessar a listagem de **Turmas** no SAPOS.
2. Aplicar o filtro por **professor** com um nome específico (no relato, o nome do próprio autor). São exibidas aproximadamente 36 entradas (em 2026/2), distribuídas em 3 páginas.
3. Remover o filtro de professor.
4. Selecionar no listbox o filtro de **PERÍODO** = 2026/2. São exibidas 138 entradas, distribuídas em 9 páginas.
5. Conferir a página 1. Ela está correta.
6. Clicar no link da **Página 2** no rodapé da tela.

## Comportamento observado

A página 2 exibida corresponde ao filtro anterior, por professor, com cerca de 36 entradas: a página 2 de 3, que mostra só as turmas daquele professor. Não aparece a página 2 de 9 com todas as turmas de 2026/2.

O autor suspeita que alterar o PERÍODO no listbox não atualiza algo relacionado aos links de paginação no rodapé da tela.

Segundo o relato, também não há uma forma clara de navegar corretamente até a página 2 da listagem geral nesse caso. O autor pretendia tentar recarregar a página algumas vezes para contornar o problema.

## Comportamento esperado

Ao clicar na Página 2 com o filtro PERÍODO = 2026/2 ativo, deve ser exibida a página 2 de 9 com todas as turmas de 2026/2. Os links de paginação devem refletir o filtro aplicado no momento.

## Stack trace / saída de erro

Não informado na issue original.

## Caso de teste

Teste manual derivado dos passos acima:

- **Pré-condição:** existem cerca de 36 turmas do professor X e 138 turmas no período 2026/2.
- **Ação:** filtrar por professor X, remover esse filtro, filtrar por PERÍODO = 2026/2 e clicar em "Página 2".
- **Verificação:** a paginação indica 9 páginas. A página 2 contém turmas de 2026/2 de qualquer professor, e não apenas as do professor X.

## Exemplo de código

Não informado na issue original.

## Versão e ambiente

- Sistema: SAPOS, listagem de Turmas.
- Período dos dados: 2026/2.
- Versão do SAPOS, navegador e sistema operacional: não informados na issue original.