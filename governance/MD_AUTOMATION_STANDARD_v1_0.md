# Padrão Oficial — Memorial Descritivo de Automação v1.0

Status: **ATIVO**  
ID: `MD_AUTOMATION_PETROBRAS_V1_0`

## 1. Modelo canônico de apresentação

O documento `MD-0249.00-6000-800-RPJ-001=C.docx` é a referência canônica de apresentação para MD de Automação.

O modelo governa **espaçamento, tipografia, estrutura e apresentação**. Em revisão de uma MD existente, o próprio arquivo de destino continua sendo a matriz física: o padrão canônico serve para auditoria de coerência e nunca autoriza transplante de layout entre documentos.

## 2. Regra de imutabilidade

A elaboração/revisão é `TEXT_ONLY`. É proibido alterar automaticamente:

- espaçamento antes/depois de parágrafos;
- espaçamento entre linhas;
- recuos, indentações e tabulações;
- alinhamentos;
- fontes, tamanhos, negrito, itálico, sublinhado e estilos do modelo;
- margens, seções e quebras estruturais;
- tabelas, linhas, células, larguras, alturas e bordas;
- cabeçalhos, rodapés, molduras, logos e assinaturas;
- posição, escala ou ancoragem de imagens e objetos;
- numeração e geometria do template.

Se a nova redação não couber, deve-se **condensar tecnicamente o texto**, nunca modificar espaçamento, fonte, tamanho ou geometria para fazê-lo caber.

As únicas exceções dinâmicas são paginação real e referências de página do índice/sumário, quando a quantidade final de folhas mudar.

## 3. Ciclo de revisão em cinza

Cor oficial: `D9D9D9`.

Antes de marcar uma nova revisão:

1. remover todo `D9D9D9` herdado de revisões anteriores;
2. identificar a mudança atual por comentário/evidência, e não pelo cinza legado;
3. aplicar cinza somente ao texto efetivamente alterado na revisão corrente;
4. aplicar o cinza de forma visualmente contínua em todo o bloco revisado, inclusive nos espaços existentes entre palavras/runs;
5. não inserir espaços, quebras ou tabs para criar continuidade visual;
6. não deixar fragmentos cinza em legendas, figuras, títulos ou parágrafos não modificados na revisão atual;
7. marcar também o título/seção e o número de página correspondente no índice quando forem afetados pela revisão atual.

O cinza é uma propriedade de **rastreabilidade da revisão corrente**, não parte permanente do conteúdo do modelo.

## 4. Hierarquia de conteúdo

A redação técnica deve ser sustentada por documentos de referência aprovados (DE, ET, LI, FD, fluxogramas, arquitetura, comentários do cliente e demais fontes do projeto). Não inventar TAG, protocolo, comando, intertravamento, capacidade ou quantitativo sem evidência.

Para comentário do cliente, a unidade de rastreabilidade é:

`comentário + trecho-âncora + folha + requisito solicitado + texto alterado + evidência técnica + status`.

## 5. Guardas obrigatórios

Toda emissão de MD deve bloquear em caso de:

- alteração de espaçamento ou `pPr` estrutural;
- alteração de fonte/tamanho/estilo não autorizada;
- alteração de tabela, seção, header/footer, imagem ou geometria;
- cinza legado remanescente fora da revisão atual;
- lacuna de cinza provocada por fragmentação de runs dentro de um bloco revisado;
- alteração atual sem cinza;
- item do índice incompatível com a revisão/paginação;
- paginação declarada diferente da renderizada;
- comentário sem rastreabilidade e evidência.

## 6. QA obrigatório

Após qualquer alteração:

1. validar pacote DOCX/ZIP;
2. comparar propriedades estruturais com a matriz;
3. confirmar que somente partes autorizadas mudaram;
4. renderizar com o renderer canônico do pipeline;
5. inspecionar visualmente **todas as páginas a 100%**;
6. bloquear a emissão em qualquer sobreposição, corte, deriva de espaçamento, quebra indevida ou marcação cinza incorreta.

## 7. Regra para novas MDs

Para uma nova MD sem matriz própria, usar o modelo canônico para a apresentação geral e preencher apenas os conteúdos do novo projeto. A quantidade de páginas é determinada pelo documento elaborado, não pela quantidade de páginas do exemplo.

## 8. Regra para MDs existentes

Para revisão de uma MD existente, não reconstruir o documento a partir do modelo. Usar o arquivo recebido como matriz física e aplicar apenas patches textuais cirúrgicos, preservando integralmente seu layout.
