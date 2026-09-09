# LESSON — Diferenciar erro, dúvida e falso positivo documental

Data: 2026-09-09
Categoria: REGRESSION
Status: ACTIVE

## Ocorrência

Durante a verificação do conjunto documental do Projeto 3501, algumas situações inicialmente foram tratadas como não conformidade embora dependessem de contexto adicional ou de uma regra de engenharia não explicitada no PDF.

## Falha conceitual

O verificador pode confundir:

- diferença gráfica com erro técnico;
- ausência de informação com não conformidade;
- hipótese de projeto com evidência;
- menor ocupação de página com falha de impressão;
- diferença entre referências comerciais permitidas por “ou similar técnico” com incompatibilidade definitiva.

## Regra preventiva

1. Marcar **ERRO** somente quando a evidência for direta, observável e demonstrável.
2. Marcar **DÚVIDA** quando a conclusão depender de decisão de engenharia, escopo, equivalência técnica, CAD/DWG, documento não fornecido ou qualquer informação ausente.
3. Nunca converter hipótese em erro.
4. Se a evidência for insuficiente, declarar o que precisa ser confirmado.
5. Comentários formais do solicitante permanecem preservados e não são descartados por interpretação do agente.

## Lições específicas incorporadas

- Símbolo de descida: exigir apenas quando houver mudança real para cota inferior.
- Elementos, ambientes e tags de outras disciplinas usados como referência devem ficar em cinza.
- Impressão: espaço em branco por menor quantidade de conteúdo não é erro; avaliar folha, enquadramento, escala, cortes, margens e legibilidade.
- ISO Full Bleed A1 deve ser verificado como padrão de impressão, não apenas por dimensões próximas de A1.
- ET/MD: correção de formatação preserva o conteúdo técnico informado.
- Matriz de Causa e Efeito: quando não aplicável ao projeto, não criar; explicar a não aplicabilidade.
- Referência “ou similar técnico”: diferença de marca/modelo é DÚVIDA até confirmação de equivalência, salvo incompatibilidade técnica objetiva.

## Testes de regressão recomendados

- Caso sem mudança de cota não pode gerar erro de símbolo de descida.
- Página com 30% de ocupação e impressão correta não pode gerar erro por espaço em branco.
- Dois modelos diferentes com “ou similar técnico” devem gerar DÚVIDA, não ERRO, se a equivalência não puder ser determinada.
- Cabeçalho com código incorreto deve gerar ERRO.
- Índice com “ERRO! INDICADOR NÃO DEFINIDO.” deve gerar ERRO.
- Achado sem evidência suficiente deve ser recusado como ERRO e rebaixado para DÚVIDA.
