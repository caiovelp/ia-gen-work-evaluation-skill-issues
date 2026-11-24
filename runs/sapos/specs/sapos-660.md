# Spec: Paginação da listagem de Turmas deve respeitar o filtro ativo

## Objetivo

Na tela de **Turmas** do SAPOS, os links de paginação no rodapé usam um filtro anterior em vez do filtro ativo.

**Cenário relatado:**
1. O usuário filtra Turmas por **professor = (nome do usuário)**. Aparecem cerca de 36 entradas em 2026/2, distribuídas em 3 páginas.
2. O usuário remove o filtro de professor e adiciona o filtro **Período = 2026/2**. Aparecem 138 entradas em 9 páginas.
3. A página 1 aparece correta.
4. Ao clicar na **Página 2**, a listagem volta ao filtro anterior (professor). Ela mostra a página 2 de 3 das turmas do usuário, e não a página 2 de 9 de todas as turmas de 2026/2.

**Hipótese do relator (não confirmada):** alterar o Período no listbox não atualiza algo ligado aos links de paginação no rodapé.

**Usuário afetado:** usuários do SAPOS que consultam Turmas com filtros. Pelo relato, isso inclui professores.

**Impacto:** o usuário não consegue navegar pelas páginas do resultado filtrado. O único contorno sugerido é recarregar a página, e não se sabe se ele funciona.

**Critérios de aceitação:**
- Depois que um filtro é aplicado, alterado ou removido, todos os links de paginação levam à página correspondente do resultado do **filtro ativo**.
- O total de páginas mostrado é igual ao número de páginas acessíveis pela navegação.
- O filtro ativo continua aplicado ao navegar entre as páginas.

## Premissas

1. O SAPOS citado é o sistema de gestão de pós-graduação de código aberto conhecido por esse nome. A versão em uso não foi informada.
2. A tela "Turmas" é uma listagem paginada com filtros de busca, incluindo professor e um listbox de Período.
3. A paginação é atualizada parcialmente, sem recarregar a página inteira, quando o filtro muda. O fato de a página 1 aparecer correta enquanto os links mantêm o estado antigo indica isso, mas não está confirmado.
4. O defeito não depende do volume de dados. Os números 36 e 138 servem só como exemplo.
5. O problema pode existir em outras listagens com o mesmo mecanismo de filtro e paginação, mas o escopo desta spec é apenas Turmas até que se confirme o contrário.
6. O comportamento esperado é o mesmo para qualquer combinação de filtros, e não só para a troca de professor por período.

## Stack Tecnológica

Não informado na issue original.

## Comandos

Não informado na issue original.
- Build: desconhecido
- Testes: desconhecido
- Lint: desconhecido
- Dev: desconhecido

## Estrutura do Projeto

Não informado na issue original. Os caminhos dos arquivos da tela de Turmas, dos filtros e da paginação são desconhecidos.

## Estilo de Código

Não informado na issue original.

## Estratégia de Testes

Os frameworks e as pastas de teste são desconhecidos. Os testes devem cobrir pelo menos:
- **Teste de regressão do cenário relatado:** aplicar o filtro A, trocar pelo filtro B e navegar para a página 2. O resultado deve corresponder ao filtro B.
- **Remoção de filtro:** remover um filtro e navegar. Os resultados não devem mais aplicar o filtro removido.
- **Combinação de filtros:** com mais de um filtro ativo, navegar e confirmar que todos continuam aplicados.
- **Recarga e retorno:** a página continua consistente após recarregar ou voltar no navegador, e o estado exibido é igual ao estado usado na paginação.
- **Nível de teste:** de preferência um teste de integração ou de sistema que percorra a interação com o filtro e o clique no link de paginação. O defeito parece estar entre a interface e o estado da busca.

## Limites

- **Sempre:**
  - Garantir que filtro exibido, resultados e links de paginação usem o mesmo estado de busca.
  - Adicionar um teste de regressão que reproduza o cenário da issue.
  - Manter o comportamento atual quando nenhum filtro é alterado.
- **Perguntar antes:**
  - Alterar o comportamento de persistência de filtros na sessão, se houver, porque isso pode afetar outras telas.
  - Aplicar a correção a outras listagens além de Turmas.
  - Atualizar ou trocar dependências de paginação ou de listagem.
- **Nunca:**
  - Remover a paginação ou elevar o limite por página como contorno.
  - Remover ou desabilitar testes existentes sem aprovação.

## Critérios de Sucesso

1. Com o filtro **Período = 2026/2** aplicado logo depois de remover o filtro de professor, clicar em "Página 2" exibe a página 2 de 9 das 138 turmas de 2026/2, e não a página 2 de 3 das turmas do professor.
2. Em qualquer página do resultado, o indicador de total de páginas e de registros corresponde ao filtro ativo.
3. Nenhum filtro removido volta a ser aplicado em qualquer navegação de paginação.
4. O filtro visível na tela é sempre o filtro aplicado aos resultados exibidos.
5. O teste de regressão falha antes da correção e passa depois dela.

## Questões em Aberto

1. Qual versão do SAPOS e qual navegador o usuário usou? O problema se reproduz em outros navegadores?
2. Como o filtro de Período foi aplicado: ao mudar o listbox, ou só depois de clicar em um botão "Buscar"/"Filtrar"? A resposta muda o ponto em que o estado deve ser atualizado.
3. Como o filtro de professor foi removido: limpando o campo, clicando em um botão de limpar, ou de outra forma?
4. A URL dos links de paginação contém os parâmetros de filtro? Que parâmetros aparecem ao passar o mouse sobre "Página 2"?
5. Os filtros ficam guardados na sessão do usuário? Se ficam, o filtro antigo vem da sessão ou dos links desatualizados?
6. Recarregar a página, como o usuário pretendia tentar, corrige os links de paginação?
7. O mesmo defeito ocorre em outras listagens do SAPOS, como Alunos ou Disciplinas? Se ocorre, a correção deve ser geral?
8. O problema ocorre só quando um filtro é trocado por outro, ou também ao aplicar o primeiro filtro e ao limpar todos?