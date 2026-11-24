## Resumo
Usuários com perfil de professor (e possivelmente de aluno) conseguem gerar no Sapos documentos assinados digitalmente, como boletins, para alunos avulsos. Isso não deveria ser possível. Só a coordenação ou a secretaria deveriam poder emitir declarações, histórico ou boletim para alunos avulsos (por exemplo, a própria declaração de aluno avulso). A issue também pede que o problema seja validado, verificando quais restrições existem hoje.

## Passos para reproduzir
Com base nas informações da issue (passos exatos não foram detalhados):
1. Entrar no Sapos com um usuário de perfil professor (ou aluno).
2. Abrir a visualização de alunos e localizar um aluno avulso.
3. Clicar no ícone de histórico ou de boletim do aluno avulso (ícones mostrados na captura de tela da issue).
4. Outro caminho: clicar no ícone de "olhinho" de um aluno avulso e, na tabela de declarações, tentar gerar um documento (captura de tela anexada à issue).

## Comportamento observado
Ao que parece, professores conseguem gerar boletins assinados digitalmente para alunos avulsos direto no Sapos. A issue não confirma se o mesmo acontece com usuários de perfil aluno, nem com histórico ou declarações.

## Comportamento esperado
O Sapos não deve emitir nenhum documento assinado digitalmente para aluno avulso quando quem pede é um usuário com perfil de aluno ou professor. Só a coordenação ou a secretaria devem poder emitir declarações, histórico ou boletim para alunos avulsos.

## Stack trace / saída de erro
Não informado na issue original.

## Caso de teste
Caso de teste mínimo derivado do comportamento esperado:
- **Dado** um aluno avulso cadastrado no Sapos
- **Quando** um usuário com perfil professor ou aluno tenta gerar um boletim, histórico ou declaração para esse aluno (pelos ícones da visualização de alunos ou pela tabela de declarações acessada pelo "olhinho")
- **Então** o sistema não deve gerar nenhum documento assinado digitalmente
- **E** quando um usuário da coordenação ou da secretaria faz a mesma ação, o documento deve ser gerado normalmente

## Exemplo de código
Não informado na issue original.

## Versão e ambiente
Não informado na issue original.