# Prompt Mestre — MD de Automação v1.0

Ao elaborar ou revisar um Memorial Descritivo (MD) de Automação:

1. Use `MD-0249.00-6000-800-RPJ-001=C.docx` como referência oficial de apresentação.
2. Em revisão de documento existente, use **o próprio documento recebido como matriz física**.
3. Modifique somente o conteúdo textual necessário. Não altere espaçamento, line spacing, recuos, tabs, alinhamentos, fontes, tamanhos, estilos, margens, tabelas, headers, footers, logos, imagens, seções ou geometria.
4. Se o texto não couber, reescreva de forma técnica e concisa. Nunca compacte o layout para fazer caber.
5. Antes de iniciar a marcação da revisão atual, remova o cinza `D9D9D9` das revisões anteriores.
6. Aplique `D9D9D9` exclusivamente ao conteúdo alterado na revisão atual e de forma contínua sobre todo o texto do bloco revisado, incluindo os espaços já existentes entre palavras/runs. Não insira espaços artificiais.
7. Atualize em cinza os itens correspondentes do índice/sumário quando título/seção/página forem afetados.
8. Atualize paginação apenas conforme a quantidade final real de páginas.
9. Interprete comentários como: trecho-âncora + nota do comentário + folha + requisito + documento afetado + ação requerida.
10. Sustente toda alteração técnica em desenhos, ET, LI, FD, fluxogramas, arquitetura e/ou demais evidências aprovadas. Não invente requisitos ausentes.
11. Após o patch, valide o DOCX estruturalmente e confirme que propriedades de parágrafo, tabelas, células, seções, headers/footers e tipografia permanecem idênticas à matriz, exceto marcação cinza atual e paginação autorizada.
12. Renderize e inspecione todas as páginas a 100%. Qualquer deriva de layout, corte, sobreposição, espaçamento alterado, cinza legado ou lacuna de marcação bloqueia a emissão.

Política normativa: `governance/MD_AUTOMATION_STANDARD_v1_0.md`.
Data Center: `datacenter/MD_AUTOMATION_STANDARD.json`.
Data Sheet: `datasheet/MD_AUTOMATION_DATA_SHEET.json`.
Script de ciclo de revisão: `pipeline/md_revision_standard.py`.
