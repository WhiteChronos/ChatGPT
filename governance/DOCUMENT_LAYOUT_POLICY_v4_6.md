# Política de Integridade de Layout Documental — v4.6

## Escopo

Aplica-se a MD, ET, LI e FD controlados no projeto AUTOMAÇÃO.

## Regra de ouro documental

O padrão visual aprovado para cada modalidade é imutável. O conteúdo técnico pertence ao documento de destino. A edição deve alterar somente texto, valores e fórmulas de conteúdo autorizadas, mantendo integralmente a estrutura visual.

## Distinção obrigatória: modelo versus documento de destino

O modelo fornece apresentação, não conteúdo nem quantidade de folhas.

- O modelo governa: geometria, fontes, tamanhos, bordas, mesclagens, alinhamentos, margens, impressão e identidade visual.
- O destino governa: código, revisão, cabeçalho, dados técnicos, quantidade de abas, paginação e documentos de referência.
- A quantidade de folhas do modelo nunca deve ser copiada automaticamente para o destino.
- A paginação final deve refletir a quantidade real do documento emitido.

## Alterações permitidas

- Texto e valores técnicos;
- TAGs, códigos e referências completas;
- Quantitativos e fórmulas de totalização previstas;
- Paginação dinâmica;
- Referências de sumário dependentes da paginação;
- Imagens técnicas somente quando expressamente aprovadas.

## Alterações proibidas

Sem autorização expressa, são proibidas alterações em margens, geometria de tabelas, largura de colunas, altura de linhas, mesclagens, bordas, preenchimentos, estilos, fontes, tamanhos de fonte, alinhamentos, cabeçalhos, rodapés, logo, assinatura, área de impressão, orientação, escala, estrutura de seções e quebras estruturais.

## LI de Entradas e Saídas

A LI E/S obedece adicionalmente ao `LI_IO_STANDARD_v1_0.md`.

Regras críticas:

- `sheet_count_source = TARGET_DOCUMENT`;
- proibir `template_sheet_count_forced = true`;
- texto inserido deve herdar o estilo da célula de destino;
- não alterar fonte/tamanho para acomodar conteúdo;
- notas gerais devem permanecer na folha de notas/resumo/referências;
- a folha de mapa de memória não pode receber nota genérica improvisada;
- os códigos de documentos devem ser completos;
- uso + reserva deve ser igual ao total;
- toda interface deve ser descrita no nível correto do protocolo.

## Data Center

O DatacenterStructureAgent deve registrar:

- Model ID;
- tipo e subtipo documental;
- fingerprint do modelo visual;
- fingerprint do arquivo-fonte do destino;
- fingerprint do arquivo emitido;
- política de quantidade de folhas;
- quantidade final de folhas;
- assinatura de estilos, células, mesclagens, dimensões, impressão e objetos;
- lista de células alteradas;
- evidências de renderização e inspeção.

Documentos Petrobras controlados não devem ser publicados em repositório público. O repositório público mantém apenas manifestos redigidos, hashes, regras e testes. O binário deve permanecer no Data Center privado autorizado.

## Data Sheet

O DataSheetConsistencyAgent deve validar:

1. coerência com MD, ET, FD, LI e desenhos;
2. TAGs, códigos, serviços, tipos, quantidades e referências;
3. origem, destino, direção e função de cada sinal;
4. somatórios de E/S;
5. protocolo na interface correta;
6. ausência de informações inventadas;
7. ausência de mutação estrutural;
8. paginação e quantidade de abas orientadas pelo destino.

## Plugins e ferramentas externas

Ferramentas descobertas no GitHub não são instaladas automaticamente. Devem passar por avaliação de licença, segurança, manutenção, determinismo, compatibilidade e teste de regressão. O catálogo é informativo até aprovação formal.

## Critério de bloqueio

Qualquer mudança estrutural não autorizada, divergência de fonte/tamanho, cópia indevida da quantidade de abas do modelo, nota fora da folha correta, paginação inconsistente ou falha de referência gera finding CRITICAL e bloqueia emissão/merge.
