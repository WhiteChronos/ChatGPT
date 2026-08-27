# Padrão Definitivo de Elaboração — LI de Entradas e Saídas — v1.0

## 1. Finalidade

Este padrão governa a criação, revisão, atualização e atendimento de comentários das Listas de Entradas e Saídas (LI E/S) da disciplina de Automação.

O padrão visual foi consolidado a partir da estrutura documental de uma LI de referência e de uma instância validada. O arquivo de referência fornece exclusivamente o padrão de apresentação. As informações técnicas e a quantidade de folhas pertencem sempre ao documento de destino.

## 2. Regra principal

O modelo define o tipo de folha, geometria, espaçamentos, células, mesclagens, linhas, bordas, fontes, tamanhos de fonte, alinhamentos, margens, cabeçalhos, rodapés, logo, área de impressão, orientação e escala.

O documento de destino define:

- código e revisão;
- cabeçalho e controle documental;
- quantidade efetiva de abas/folhas;
- TAGs, serviços, sinais, endereços, origens, destinos e notas;
- quantitativos de E/S;
- documentos de referência;
- conteúdo do mapa de memória.

Nunca copiar a quantidade de abas do arquivo usado como referência visual. A quantidade de abas é determinada pelo conteúdo e pela emissão do documento de destino.

## 3. Alterações permitidas

Somente são permitidas:

- substituição ou inclusão de texto técnico nas células previstas;
- atualização de código, revisão, título, cliente, programa, área, SS, IN, contrato e responsáveis;
- atualização de TAGs, serviços, tipos de E/S, endereços, alimentação, contato, operação, redundância e notas;
- atualização de quantitativos e fórmulas de totalização já previstas pelo padrão;
- atualização da paginação “X de Y” conforme a quantidade real de folhas;
- atualização de referências documentais completas;
- correção de ortografia ou nomenclatura técnica sem mudança de layout.

## 4. Alterações proibidas

É proibido, salvo autorização expressa e registrada:

- alterar largura de coluna ou altura de linha;
- inserir, remover ou deslocar linhas/colunas para acomodar texto;
- alterar mesclagens;
- alterar bordas, espessuras, estilos ou tipos de linha;
- alterar fontes, tamanhos de fonte, negrito, itálico ou alinhamentos do padrão;
- alterar margens, orientação, escala, área de impressão, cabeçalhos ou rodapés;
- mover, redimensionar ou substituir logo e objetos gráficos;
- criar abas apenas para igualar a quantidade de folhas do arquivo-modelo;
- incluir notas explicativas improvisadas na folha de mapa de memória ou na última folha;
- reduzir fonte para fazer texto excessivo caber.

Quando o conteúdo não couber, a redação deve ser tecnicamente condensada, sem perda de sentido e sem deformar o modelo.

## 5. Quantidade de abas e paginação

A quantidade de abas é orientada pelo documento de destino, não pelo padrão visual.

A emissão deve conter somente as folhas necessárias ao seu conteúdo. A paginação deve ser sequencial e coerente em todas as abas. A folha de capa e cada folha interna devem declarar o mesmo total final.

Abas de detalhe podem ser repetidas somente quando a quantidade real de pontos exigir. Abas vazias ou criadas apenas para reproduzir a contagem do modelo são proibidas.

## 6. Arquétipos de folha

O padrão prevê os seguintes arquétipos funcionais:

1. Capa e índice de revisões;
2. Lista de pontos de E/S;
3. Notas, resumo de pontos e documentos de referência;
4. Mapa de memória/interface de equipamentos;
5. Folhas adicionais de E/S somente quando a quantidade real de pontos exigir.

O nome da aba pode seguir a convenção do documento de destino, desde que a função da folha permaneça rastreável.

## 7. Regra para notas

Notas gerais, explicações de protocolo, critérios de aplicação e documentos de referência devem permanecer na folha destinada a “Notas, Resumo e Documentos de Referência”.

A folha de mapa de memória deve conter apenas TAG, descrição, interface/tipo de sinal e informações diretamente ligadas ao mapeamento. Não inserir linha genérica “NOTA” no final dessa folha.

## 8. Regras técnicas mínimas

- Toda E/S deve possuir identificação, tipo, serviço, origem/destino ou controlador associado e evidência documental.
- CMD, RUN, FAULT e AVAILABLE não podem ser inferidos entre si.
- Intertravamentos devem indicar causa, efeito, estado seguro e documento-fonte.
- Códigos de desenhos e documentos devem ser completos.
- O resumo de pontos deve satisfazer: quantidade em uso + reserva instalada = quantidade total.
- O tipo de protocolo deve representar a interface correta. Protocolo nativo do equipamento não deve ser confundido com o protocolo Gateway–PLC.
- Informação dependente do equipamento deve usar “quando disponível/aplicável” quando não for universal.

## 9. Fluxo obrigatório

1. Identificar o arquivo de destino e sua quantidade real de folhas.
2. Carregar o padrão LI E/S como referência visual.
3. Inventariar fontes: desenhos, MD, ET, FD, comentários e listas relacionadas.
4. Mapear o conteúdo do destino para os arquétipos do padrão.
5. Alterar somente valores/textos nas células previstas.
6. Atualizar fórmulas e paginação.
7. Validar TAGs, tipos de sinal, origem/destino, endereços e referências.
8. Comparar assinatura estrutural do arquivo antes/depois.
9. Renderizar todas as folhas.
10. Inspecionar visualmente todas as folhas.
11. Bloquear emissão se houver mudança de layout, fonte ou paginação incoerente.
12. Registrar evidências no Data Center e no Data Sheet.

## 10. Identificação do modelo

- Model ID: `LI_IO_PETROBRAS_AUTOMACAO_V1_0`
- Política de quantidade de folhas: `TARGET_DOCUMENT_DRIVEN`
- Regime de qualidade: `BLOCK_ON_ANY_FAILURE`
- Binário controlado: armazenado somente em repositório privado/Data Center autorizado.
- Repositório público: armazena apenas manifesto redigido, hashes, regras e testes; não publica documentos Petrobras controlados.
