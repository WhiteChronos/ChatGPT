# Política de Integridade de Layout Documental — v4.5

## Escopo
Aplica-se aos documentos de engenharia controlados do projeto AUTOMAÇÃO:

- MD — Memorial Descritivo;
- ET — Especificação Técnica;
- LI — Lista de Instrumentos / Materiais / Cabos / Entradas e Saídas;
- FD — Folha de Dados / Data Sheet.

## Regra de Ouro Documental
O arquivo original aprovado para cada modalidade é a matriz de layout e deve permanecer intocado.

A elaboração, revisão ou atendimento de comentários pode alterar somente o conteúdo técnico necessário, preservando integralmente a estrutura visual e documental do arquivo-fonte.

## Alterações permitidas
- Texto existente;
- Valores técnicos;
- Códigos, TAGs e referências;
- Quantitativos textuais;
- Imagens técnicas somente quando expressamente aprovadas;
- Paginação dinâmica necessária para refletir a quantidade final de folhas;
- Referências de página no sumário quando a paginação final mudar.

## Alterações proibidas
Salvo solicitação explícita do responsável pelo documento, são proibidas alterações em:

- margens;
- geometria de tabelas;
- largura de colunas;
- altura de linhas;
- mesclagens;
- bordas;
- preenchimentos;
- estilos;
- fontes;
- alinhamentos estruturais;
- cabeçalhos;
- rodapés;
- logo;
- assinatura;
- área de impressão;
- orientação da página;
- escala de impressão;
- estrutura de seções;
- quebras estruturais do template.

## Regra específica para Excel / Data Sheet
Para LI e FD, o layout interno da planilha é considerado parte do padrão documental. O conteúdo deve ser adaptado ao espaço existente sem redimensionar colunas, linhas ou células.

Quando o texto não couber, a solução deve priorizar redação técnica mais concisa e compatível com a célula existente. Não é permitido deformar o template para acomodar o conteúdo.

## Regra específica para Word
Para MD e ET, o documento deve ser editado preservando estilos, tabelas, margens, cabeçalhos, rodapés, imagens e demais objetos do modelo. O texto pode ser substituído ou complementado apenas nos pontos necessários.

## Paginação dinâmica
A quantidade total de folhas é variável e deve refletir o documento final efetivamente emitido.

São permitidas e obrigatórias, quando aplicáveis:

- atualização de “Folha X de Y”;
- atualização do total de páginas/folhas;
- atualização das páginas do sumário;
- atualização de referências internas dependentes da paginação.

A paginação é a única exceção automática à imutabilidade estrutural do layout.

## Data Center / Registro de Template
O DatacenterStructureAgent deve registrar, para cada documento controlado:

- tipo documental;
- código e revisão;
- hash/fingerprint do template original;
- quantidade de folhas original;
- componentes estruturais protegidos;
- lista de alterações autorizadas;
- quantidade final de folhas após a revisão;
- evidências de validação.

Uma nova revisão nunca deve sobrescrever silenciosamente o padrão anterior. O histórico deve ser versionado.

## Data Sheet / LI / FD
O DataSheetConsistencyAgent deve:

1. preservar o layout interno da planilha;
2. validar TAGs, códigos, descrições, quantidades e referências;
3. cruzar o conteúdo com desenhos, MD, ET e FD/LI relacionados;
4. bloquear qualquer mudança de layout não autorizada;
5. confirmar que a paginação declarada corresponde à emissão final;
6. registrar divergências como finding antes da emissão.

## Critério de bloqueio
Qualquer alteração estrutural não autorizada deve gerar finding CRITICAL e bloquear a emissão ou merge.

A política opera em regime BLOCK_ON_ANY_FAILURE para violações de layout e paginação.
