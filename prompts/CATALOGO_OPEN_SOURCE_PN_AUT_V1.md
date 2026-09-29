# Catalogo pesquisado - PN-AUT / GitHub / Codex

**Consulta: 2026-09-28. Estado: pesquisa e proposta; nao instalacao ou homologacao.**

Curadoria por funcao, nao busca exaustiva de todos os repositorios. Cada versao selecionada ainda precisa de pin, revisao de licenca/seguranca e teste de integracao.

| Repositorio | Aplicacao proposta | Limite relevante |
|---|---|---|
| [CadQuery/cadquery](https://github.com/CadQuery/cadquery) | Modelagem parametrica Python, montagem e exportacao STEP. | Importar CAD oficial; uma caixa com medidas corretas nao substitui detalhes oficiais. |
| [FreeCAD/FreeCAD](https://github.com/FreeCAD/FreeCAD) | Importacao CAD, montagem e vistas tecnicas. | Alternativa ao motor principal, nao instalar varios motores sem necessidade. |
| [gumyr/build123d](https://github.com/gumyr/build123d) | Modelagem CAD parametrica em Python. | Selecionar por compatibilidade com a equipe e testar exportacao. |
| [mozman/ezdxf](https://github.com/mozman/ezdxf) | Leitura/escrita DXF e dados vetoriais. | DXF 2D nao fornece automaticamente um modelo 3D completo. |
| [mikedh/trimesh](https://github.com/mikedh/trimesh) | Inspecao de malhas, cenas e limites geometricos. | Bounding box e malha nao comprovam sozinhos a fidelidade BRep. |
| [blender/blender](https://github.com/blender/blender) | Render de uma montagem congelada, materiais, luz e cameras. | Mirror do projeto Blender; geometria e escala devem ser verificadas antes/depois. |
| [python-pillow/Pillow](https://github.com/python-pillow/Pillow) | Composicao em pixels, leitura de dimensoes, canais e alfa. | Nao reconstruir dimensoes fisicas a partir de pixels deformados. |
| [libvips/libvips](https://github.com/libvips/libvips) | Processamento de imagens grandes com avaliacao sob demanda. | Recursos da maquina e limites do formato continuam exigindo controle. |
| [Kozea/CairoSVG](https://github.com/Kozea/CairoSVG) | Rasterizacao SVG para PNG em resolucao definida. | Fixar versao/fontes e impedir resize independente na exportacao. |
| [linebender/resvg](https://github.com/linebender/resvg) | Renderizacao SVG. | URL atual consultada; alternativa a CairoSVG, nao validador CAD. |
| [ImageMagick/ImageMagick](https://github.com/ImageMagick/ImageMagick) | Operacoes de imagem, composicao e comparacao. | Bloquear opcoes de deformacao/crop para vistas dimensionais. |
| [opencv/opencv](https://github.com/opencv/opencv) | Mascaras, contornos e comparacao de imagem. | Visao computacional nao prova dimensoes/quantidades oficiais sem modelo. |
| [pytest-dev/pytest](https://github.com/pytest-dev/pytest) | Testes unitarios, integracao e contratos executaveis. | Executar os comandos reais e separar testes de fixture de projeto completo. |
| [HypothesisWorks/hypothesis](https://github.com/HypothesisWorks/hypothesis) | Testes baseados em propriedades para unidades, escalas e quantidades. | Geradores precisam representar invariantes e casos invalidos do projeto. |
| [microsoft/playwright](https://github.com/microsoft/playwright) | Testes de navegador, captura e fluxos de exportacao. | Usar quando houver HTML/visualizador; nao prova geometria sozinho. |
| [google/or-tools](https://github.com/google/or-tools) | Solver para posicionamento com restricoes. | Nao permitir escala de componente como variavel de otimizacao. |
| [cdelker/schemdraw](https://github.com/cdelker/schemdraw) | Esquemas eletricos vetoriais gerados por codigo. | Simbolos e logica requerem validacao tecnica; nao certifica normas. |
| [qelectrotech/qelectrotech-source-mirror](https://github.com/qelectrotech/qelectrotech-source-mirror) | Editor de esquemas eletricos. | Mirror; verificar fluxo de arquivos e biblioteca antes de integrar. |
| [IfcOpenShell/IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell) | Leitura/geracao IFC e ecossistema Bonsai para Blender. | IFC executado nao equivale a Revit executado. |
| [pyrevitlabs/pyRevit](https://github.com/pyrevitlabs/pyRevit) | Automacao e ferramentas sobre Revit. | Requer ambiente Revit autorizado; ponte open source nao torna Revit livre. |
| [Autodesk/revit-ifc](https://github.com/Autodesk/revit-ifc) | Ferramentas oficiais Autodesk para intercambio IFC/Revit. | Reverificar compatibilidade com a versao de Revit e unidades. |
| [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp) | Ponte de controle para FreeCAD por MCP. | Nao nativa desta conversa; auditar execucao de codigo, permissoes e runtime local. |
| [ahujasid/mcp-for-blender](https://github.com/ahujasid/mcp-for-blender) | Ponte de controle para Blender por MCP. | URL atual consultada apos redirecionamento de blender-mcp; nao e conector oficial OpenAI/Blender. |
| [github/github-mcp-server](https://github.com/github/github-mcp-server) | Servidor MCP do GitHub. | Conector GitHub desta conversa ja esta disponivel; nao duplicar por obrigacao. |
| [openai/codex-action](https://github.com/openai/codex-action) | Executar Codex com prompt versionado em GitHub Actions. | Credencial/runner/permissoes e seguranca necessarios; nao substituir CI independente. |
| [openai/skills](https://github.com/openai/skills) | Catalogo de Skills para Codex. | Consultar caminhos e instalar explicitamente; existencia no repo nao significa descoberta. |
| [obra/superpowers](https://github.com/obra/superpowers) | Metodos de depuracao, planejamento, TDD e verificacao. | Processo de trabalho nao substitui geometria oficial nem auditoria do artefato. |
| [github/awesome-copilot](https://github.com/github/awesome-copilot) | Colecao com skill github-actions-hardening para revisao de workflows. | Compatibilidade e comportamento no ambiente Codex devem ser verificados antes da ativacao. |

## Conjunto inicial recomendado

CadQuery OU FreeCAD para geometria; Blender para render; SVG mais CairoSVG/resvg para cotas e tabelas; Pillow para composicao sem resize; pytest e Hypothesis para QA. Adicionar libvips para imagens grandes, OR-Tools quando o layout tiver fontes completas e IFC/Revit somente se houver demanda BIM.

## Skills

Usar uma unica implementacao Python canonica e wrappers curtos em SKILL.md. Expor via .agents/skills ou plugin registrado conforme a documentacao do Codex. Propostas: pn-aut-source-audit, pn-aut-canonical-geometry, pn-aut-cable-entry-audit, pn-aut-render-compose e pn-aut-delivery-audit. Ainda nao criadas/instaladas por este pacote.

## Plugins e conectores

A consulta ao diretorio por Blender/FreeCAD/Revit/CAD/BIM nao retornou um conector direto. GitHub e OpenAI Developers foram encontrados instalados. As pontes MCP de terceiros acima requerem ambiente de execucao proprio e auditoria; nao estao habilitadas por esta pesquisa. Nenhuma permissao ou instalacao foi alterada.

## Fonte mecanica decisiva

NSYCRN86300: gabinete nominal 600 x 800 x 300 mm, uma porta e uma placa de entrada de cabos. Oito prensa-cabos pertencem ao registro da LI R02 consultada, nao a uma confirmacao de fornecimento de fabrica. Preservar a LI e verificar separadamente o projeto de furacao.

## Referencias oficiais

- [Schneider NSYCRN86300 - composicao, dimensoes e recursos tecnicos](https://eshop.se.com/sa/nsycrn86300-spacial-crn-plain-door-w-o-mount-plate-h800-w600-d300-ip66-ik10ral7035.html)
- [Codex GitHub Action](https://developers.openai.com/codex/github-action)
- [Codex GitHub integration](https://developers.openai.com/codex/integrations/github)
- [Codex Skills](https://developers.openai.com/codex/skills)
- [GitHub secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
- [GitHub pull_request_target security](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)
