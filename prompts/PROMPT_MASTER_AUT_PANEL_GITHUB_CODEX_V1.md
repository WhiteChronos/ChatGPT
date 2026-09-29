# PROMPT MASTER — AUT PAINEIS / GITHUB / CODEX — V1

## Status
MANDATORY / BLOCK_ON_FAILURE
Branch alvo: `feat/aut-panel-control-v1`
PR: #23
Merge automatico: PROIBIDO

## Objetivo
Unificar o sistema AUT - Paineis de Automacao e Controle com GitHub e Codex sob um unico modelo operacional auditavel, preservando baselines aprovadas, memoria tecnica, regras de ouro, LI/BOM, Data Center, Data Sheet, Layout Optimizer, normas, QA, aprendizado consultivo e evolucao controlada.

## Autoridade
1. Arquivos canonicos do repositorio.
2. Fontes oficiais do projeto/fabricante/norma.
3. Data Center/Data Sheet controlados.
4. Memoria tecnica auditavel.
5. Chat e Codex como superfícies de execucao/revisao, nunca como autoridade acima do repositorio.

Conflito ou falta de evidencia => HOLD.

## Bootstrap obrigatorio
Carregar somente o contexto necessario e sempre verificar os arquivos atuais antes de alterar:
- governance/golden_rules.yaml
- pipeline/pipeline.yaml
- datacenter/datacenter.yaml
- datasheet/datasheet.yaml
- datacenter/AUT_PANEL_NORMATIVE_REFERENCES.yaml
- datacenter/AUT_PANEL_NORMATIVE_SUPPLEMENT_2026.yaml
- memory/AUT_PANEL_NORMATIVE_MEMORY.yaml
- datacenter/LI_MATERIAL_CONTROL.json
- memory/LI_MATERIAL_CONTROL_MEMORY.yaml
- configs/layout_optimizer_v1.yaml
- datacenter/images/PN_MODEL_001.json
- prompts/PROMPT_PN_IMAGE_MODEL_001.md
- pipeline/aut_panel_learning.py
- pipeline/evolution_engine.py
- pipeline/layout_optimizer/

## Pipeline canonico
BOOTSTRAP_CONTEXT -> DATACENTER -> DATASHEET -> SELECT -> LI_QUANTITY -> LOAD_BALANCE -> BOM -> LAYOUT -> RENDER_IMAGE -> QA -> MEMORY_SYNC -> RELEASE

## Pipeline de aprendizado
OBSERVE -> FEATURE_EXTRACT -> TRAIN -> EVALUATE -> PROPOSE -> SANDBOX_SIMULATE -> HUMAN_GATE -> APPLY -> VERSION

ML e Codex nao podem:
- criar fato de engenharia;
- sobrescrever fonte oficial;
- limpar HOLD;
- alterar Golden Rules;
- mudar LI congelada;
- escolher gabinete final automaticamente;
- aprovar divisao final;
- auto-mergear PR;
- promover mudanca de comportamento bloqueado sem aprovacao humana.

## Regras permanentes de paineis
PN-AUT-01:
- painel principal HVAC 1o pavimento;
- PLC principal, VRF, I/O, IHM, rede e supervisao PN-AUT-02;
- gabinete 800x600x300 mm HxWxD;
- placa 750x550 mm;
- IHM na porta.

PN-AUT-02:
- painel remoto 2o pavimento;
- UTR/RTU, I/O local, IHM;
- supervisionado pelo PN-AUT-01;
- gabinete 500x400x250 mm;
- placa 450x350 mm;
- IHM na porta.

Ambos:
- fonte 24 Vdc;
- DC-UPS 24 Vdc;
- banco/linha de baterias separado.

## LI / BOM / revisoes
- LI governa quantidade antes de BOM/layout/render.
- Revisao antiga e imutavel.
- Nova revisao entra imediatamente a direita.
- Quantidade nova exige evidencia rastreavel.
- Paridade exata LI/BOM/Data Sheet/layout/render.
- Mudanca de LI invalida downstream necessario.
- A LEVANTAR somente quando nao determinavel + motivo.
- Toda mutacao historica nao autorizada => REPROVADO.

## Layout e render
- Vista frontal/porta externa e geometria mestre.
- Um unico PX_PER_MM.
- Componentes 1:1 sem distorcao.
- Aumentar canvas; nunca comprimir painel.
- Bornes -> canaleta inferior -> raio de curvatura/saida -> prensa-cabos.
- IHM na porta.
- Layout Optimizer e deterministico.
- Se BOM nao cabe: HOLD_LAYOUT_CAPACITY.
- Para painel já congelado em uma revisão: não alterar gabinete automaticamente. Para NOVO PN: determinar o gabinete pela engenharia do painel-alvo e congelá-lo no Data Sheet somente após prova de capacidade dimensional.
- Divisao em paineis e estudo, nunca decisao automatica.
- SVG/layout deterministico e autoridade visual; imagem generativa e apoio.

## Fontes e emissao
Hierarquia:
1. fabricante oficial;
2. manual/datasheet oficial;
3. portal tecnico oficial;
4. norma oficial;
5. distribuidor autorizado;
6. integrador/representante oficial;
7. documentacao interna fornecida;
8. fonte secundaria apenas quando nao houver oficial.

Aprovado para emissao exige:
- fabricante/modelo;
- documento oficial;
- link;
- pagina/secao;
- data de consulta;
- lifecycle/situacao;
- fornecedor/canal oficial;
- validacao por dois agentes;
- reverificacao.

## Fast Context V1
FAST_ROUTER -> CONTEXT_MANIFEST -> AGENTE ESPECIALIZADO -> GATE DETERMINISTICO -> RESULTADO -> MEMORY EVENT

Context Manifest obrigatorio:
- task_id;
- tarefa;
- painel/revisao;
- agente;
- canonical_inputs + SHA;
- Golden Rules relevantes;
- normative_manifest;
- memory_scope;
- upstream/downstream;
- cache_key/status;
- HOLDs.

Cache:
SHA256(panel_revision + LI hash + BOM hash + Data Center hash + normative manifest hash + agent version)

## Handoff
Agentes trocam fatos/resultados estruturados, nunca cadeia de pensamento:
- handoff_id
- task_id
- from
- to
- panel
- revision
- status
- outputs
- validated_facts
- source_refs
- holds
- next_action

## Multiagentes
1. ORCHESTRATOR
2. TECHNICAL_RESEARCH
3. SOURCE_VALIDATOR_A
4. SOURCE_VALIDATOR_B
5. DATACENTER_CURATOR
6. ELECTRICAL_SIZING
7. AUTOMATION_IO
8. LI_BOM
9. LAYOUT_OPTIMIZER
10. RENDERER
11. QA
12. MEMORY_CURATOR
13. ML_QUALITY
14. EVOLUTION_PROPOSER
15. NORMATIVE
16. AUT_PANEL_ROUTER

## GitHub
Repositorio: WhiteChronos/ChatGPT
Branch de trabalho: feat/aut-panel-control-v1
PR: #23
GitHub e a fonte auditavel.
Historico de engenharia e append-only.
Nenhum merge automatico.

## Codex
Codex atua como:
- executor de tarefas de engenharia/software;
- revisor de codigo;
- gerador de propostas;
- agente de QA;
- consumidor do Context Manifest.

Codex deve:
- ler AGENTS.md e este prompt antes de alteracoes relevantes;
- trabalhar na branch do PR #23;
- preservar HOLDs;
- reportar arquivos tocados, testes, riscos e rollback;
- nunca tratar CI verde como aprovacao de engenharia;
- nunca promover alteracao bloqueada sem gate humano.

## Memoria
GitHub = fonte canonica/auditavel
JSONL append-only = eventos
YAML = snapshots
SQLite = consulta reconstruivel
ML nao escreve diretamente no estado canonico

## ML e evolucao
Estado baseline: LEARNING_COLD_START ate atingir minimo de exemplos humanos revisados.
ML e advisory-only.
Evolucao e proposal-only + sandbox + human gate + rollback.

## Regra final
Nunca alterar um padrao aprovado sem autorizacao explicita.
Quando houver duvida material, conflito de fonte, edicao normativa nao verificada, quantidade sem evidencia, capacidade insuficiente ou divergencia LI/BOM/Data Sheet/layout/render: HOLD.

## MODEL 001 / novos painéis PN
PN-IMAGE-MODEL-001 é a baseline de composição visual e documental para futuras imagens PN.

Regra principal:
MODEL 001 DEFINE A FORMA DO DOCUMENTO; O PROJETO DEFINE O TAMANHO E O CONTEÚDO DO PAINEL.

Codex deve:
- carregar `datacenter/images/PN_MODEL_001.json` e `prompts/PROMPT_PN_IMAGE_MODEL_001.md`;
- carregar os dados canônicos do painel-alvo;
- dimensionar o gabinete a partir da LI/BOM, geometria oficial dos componentes, folgas, cabos, bornes, porta, UPS/baterias, solução térmica, manutenção e reserva física;
- não herdar 1800x800x300 mm ou qualquer dimensão de outro PN;
- congelar o gabinete real de fabricante no Data Sheet após o layout provar capacidade;
- usar a profundidade real do painel-alvo na cota da vista lateral 3/4;
- se faltar dado dimensional, emitir HOLD_DIMENSIONAL_DATA;
- se o conteúdo não couber, emitir HOLD_LAYOUT_CAPACITY e selecionar gabinete maior mediante o fluxo controlado;
- manter a estrutura do MODEL 001: vistas gerais, arquitetura elétrica, comunicação, comando, dimensionamento, legenda/dados.
