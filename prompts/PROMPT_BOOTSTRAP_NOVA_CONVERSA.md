# PROMPT PARA COLAR EM UMA NOVA CONVERSA — AUTOMAÇÃO EQUIPAMENTO

Você está continuando o projeto **AUTOMAÇÃO EQUIPAMENTO**. Não trate esta conversa como projeto novo e não reconstrua regras por memória informal.

## Bootstrap obrigatório
Antes de executar qualquer tarefa técnica, carregue os seguintes arquivos do pacote/repositório e valide seus vínculos:

- `prompts/PROMPT_MASTER_AUT_PANEL.md`
- `governance/golden_rules.yaml`
- `pipeline/pipeline.yaml`
- `pipeline/conversation_contract.py`
- `datacenter/datacenter.yaml`
- `datasheet/datasheet.yaml`
- `templates/panel_template.yaml`
- `context/AUT_PANEL_CONVERSATION_MEMORY.yaml`

Se você tiver acesso ao repositório, use a versão mais recente da branch de trabalho indicada em `context/AUT_PANEL_CONVERSATION_MEMORY.yaml`. Se não tiver acesso ao repositório, use o ZIP operacional fornecido pelo usuário. Se os arquivos não estiverem disponíveis, peça o pacote e **não invente o estado do projeto**.

Quando houver ambiente de código, execute primeiro:

`python pipeline/conversation_contract.py validate`

Só prossiga se o contrato retornar `PASS`.

## Fonte de verdade
Obedeça a seguinte precedência:

1. `governance/golden_rules.yaml`
2. `pipeline/pipeline.yaml`
3. `datacenter/datacenter.yaml`
4. `datasheet/datasheet.yaml`
5. LI vigente do painel
6. `templates/panel_template.yaml`
7. `context/AUT_PANEL_CONVERSATION_MEMORY.yaml` para estado entre conversas
8. conversa atual

Conversa e memória não podem sobrescrever Data Center/Data Sheet sem mudança autorizada.

## Regra central
Use a sequência:

`BOOTSTRAP_CONTEXT → DATACENTER → DATASHEET → SELECT → LI_QUANTITY → LOAD_BALANCE → BOM → LAYOUT → RENDER_IMAGE → QA → MEMORY_SYNC → RELEASE`

A LI é a única fonte de quantidade. A imagem nunca cria quantidade. A IHM fica na porta. Dimensões não podem ser distorcidas. Divergência de quantidade/geometria/hash/padrão é `REPROVADO`. Falta de dado técnico é `HOLD`.

## Memória compartilhada
A memória operacional entre esta conversa e a anterior é:

`context/AUT_PANEL_CONVERSATION_MEMORY.yaml`

Leia o `memory_id`, `mutable_state`, `open_holds`, `active_work` e `history`. Ao concluir um marco técnico ou uma decisão autorizada, atualize esse arquivo e incremente `sync_revision`. Não altere `immutable_contract` sem autorização explícita.

## Comandos especiais
### `/explaincode <arquivo ou trecho>`
Explique o código em partes, sem modificar. Mostre finalidade, fluxo, funções, entradas/saídas, invariantes, Regras de Ouro, riscos e vínculo com pipeline/Data Center/Data Sheet.

### `/refactor <arquivo ou trecho>`
Melhore a estrutura do código sem mudar o comportamento esperado. Preserve interfaces, IDs, regras, quantidades e contratos. Rode testes/QA antes de considerar concluído. Se o alvo for arquivo bloqueado, peça autorização explícita antes de editar.

## Primeira resposta obrigatória na nova conversa
Antes da tarefa solicitada, responda de forma curta com:

- `memory_id` carregado;
- `pipeline_id` carregado;
- `standard_id` carregado;
- branch/PR ativos, se registrados;
- painel e revisão de LI ativos;
- resultado do bootstrap (`PASS`, `HOLD` ou `REPROVADO`).

Depois execute a tarefa do usuário conforme o padrão mestre.
