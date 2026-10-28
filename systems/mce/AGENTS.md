# Sistema MCE — regras locais exclusivas

Escopo: sistema de engenharia de Matriz de Causa e Efeito, independente de motor de engenharia reversa, MCP e interface Web.

1. Inventariar modelo mestre XLSX, P&IDs, I/O, narrativas, especificações, SRS e revisões com SHA-256.
2. Identificar Projeto e SS somente quando documentados. Não inferir setpoints, TAGs, trips, votações, alarmes ou SIFs.
3. Apresentar relatório de entendimento e PARAR em `ANALISADO_AGUARDANDO_DECISAO`.
4. Mediante autorização expressa, contrato de células permitido e modelo validado, editar exclusivamente texto documentado em CÓPIA do Excel.
5. Não alterar cabeçalho, estilos, fórmulas, mesclas, imagens, áreas de impressão ou artefatos não autorizados. Sinalizar alterações válidas em cinza `D9D9D9`.
6. No máximo 50 causas por folha (ou menos quando modelo limitar). Auditar OOXML e SHA da fonte e apresentar como preliminar à validação multidisciplinar.
7. Exportações P&ID OCR/grafo são auxiliares e exigem verificação humana por fonte/arquivo/revisão; nunca geram comandos de segurança.
8. Não importar módulos de outros produtos para executar este workflow. Não publicar documentos privados.
