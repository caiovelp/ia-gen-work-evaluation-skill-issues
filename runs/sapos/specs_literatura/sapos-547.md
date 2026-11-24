## Resumo
A funcionalidade de envio de boletim na notificação parece não funcionar desde a mudança nos mecanismos de geração de boletim. Essa funcionalidade gera o boletim e o anexa à notificação. Ela é ativada por uma opção de seleção na configuração da notificação, mostrada em uma captura de tela na issue original.

## Passos para reproduzir
1. Configurar uma notificação no Sapos.
2. Marcar a opção que ativa o envio de boletim na notificação (mostrada na captura de tela da issue original: https://github.com/user-attachments/assets/6f33446e-5b7f-4896-906e-e64da655d2be).
3. Fazer a notificação ser enviada.
4. Verificar se o boletim foi gerado e anexado à notificação.

## Comportamento observado
A funcionalidade parece não funcionar depois da mudança nos mecanismos de geração de boletim. A issue não descreve exatamente o que acontece, por exemplo se a notificação chega sem anexo ou se ocorre algum erro.

## Comportamento esperado
Com a opção marcada, o boletim deve ser gerado e anexado à notificação enviada.

## Stack trace / saída de erro
Não informado na issue original.

## Caso de teste
Não informado na issue original.

## Exemplo de código
Não informado na issue original.

## Versão e ambiente
Não informado na issue original. A issue diz apenas que o problema começou depois da mudança nos mecanismos de geração de boletim.