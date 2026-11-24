## Resumo
Popular a aplicação com um exemplo padrão de processo seletivo, já configurado e customizável.

## Descrição
Criar um exemplo padrão de processo seletivo que outros programas (e desenvolvedores) possam customizar. O exemplo deve reproduzir o processo usado atualmente no IC, com as características abaixo.

**Estrutura geral**
- Edital de seleção com formulário de candidatura (sem carta) e duas fases: homologação e avaliação.
- Ranking padrão com os seletores "Ampla concorrência", "Racial" e "PcD", ordenado por "Nota final" e "Média da formação acadêmica".
- Ranking de bolsas com um único seletor e com a condição de que o candidato tenha solicitado bolsa. Usa os mesmos critérios de ordenação do ranking padrão.

**Fase de homologação**
- Formulário com os campos "Optante negro ou indígena", "PcD", "Homologação" e "Razão de indeferimento".
- Consolidação com envio de e-mail de notificação de deferimento ou indeferimento.
- Condição para aprovação: "Homologação" = "Deferida".
- Comitê formado por usuários com papel de secretaria. Na migração, pode-se usar apenas um desses usuários. Se não existir nenhum, usar o admin.

**Fase de avaliação**
- Formulário com os campos "Nota da formação acadêmica", "Nota da experiência acadêmica e profissional" e "Observação".
- Consolidação com cálculo de "Média da formação acadêmica", "Média da experiência acadêmica e profissional" e "Nota final".
- Condição para aprovação: "Nota final" >= 6.
- Comitê formado, na migração, pelo usuário admin. O comitê deveria ser composto por professores, mas o autor considera mais "seguro" usar o admin nesta configuração padrão.

## Versão do produto
Não informado na issue original.

## Justificativa
Um exemplo configurado facilitaria que outros programas e desenvolvedores usem a funcionalidade de edital/processo seletivo. Eles partiriam de uma configuração pronta e a customizariam, em vez de montar tudo do zero.

## Caso de uso ou cenário
Um programa (ou desenvolvedor) que quer usar a parte de edital seletivo parte do exemplo padrão, baseado no processo do IC. Em seguida, ajusta o exemplo às próprias necessidades, como formulários, fases, rankings, condições de aprovação e comitês.

## Solução possível
Popular o sistema, por exemplo por meio de uma migração, com um processo seletivo padrão que reproduz o processo atual do IC:
- Edital com formulário de candidatura (sem carta) e fases de homologação e avaliação.
- Os rankings padrão e de bolsas descritos acima.
- Os formulários, consolidações, condições de aprovação e comitês de cada fase descritos acima.
- Na migração, o comitê da homologação recebe um usuário com papel de secretaria (ou o admin, se não houver nenhum) e o comitê da avaliação recebe o admin.