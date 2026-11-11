# Ferramenta Matriz de Causa e Efeito — DataCenter compartilhado do MCE

**Produto:** MCE_INDEPENDENTE; **Skill única de entrada:** `matriz-causa-efeito`. Este documento descreve o **pipeline operacional pré-análise**. O SQLite e os eventos são os mesmos de `scripts/mce_memory.py`; o novo DataSheet é uma visão *por execução*, sem banco independente. A memória canônica versionada continua em `spec/memoria.md` e Issue #120.

## Três repositórios auxiliares, sem execução de código de terceiros

| Adaptador local | Repositório de referência | Entrada já suportada | Limitação de engenharia |
| --- | --- | --- | --- |
| `azure` | `Azure-Samples/digitization-of-piping-and-instrument-diagrams` | JSON `assets[].connections[]` | Topologia não é intertravamento |
| `houston` | `S-Houston/digitised-pid-mlops` | CSV `filename,consolidated_text` | OCR não é TAG nem setpoint validado |
| `industrial` | `ZzzJjt/Industrial-Control` | JSON didático `causes`, `effects`, `interlock_matrix` | Apenas benchmark não normativo, **nunca** relação de segurança do projeto |

Os adaptadores são próprios do MCE, originalmente implementados em `engenharia-mce-projeto/scripts/pid_bridge.py`. Nenhum código, modelo ou API desses repositórios é executado/clonado/enviado; `industrial` é exemplo independente, não lógica PLC/SIS. Licenças de `S-Houston` e `Industrial-Control` não estão comprovadas para redistribuição de fontes.

## 1. Preparar o workspace *fora do GitHub*

O workspace real, DataSheet e SQLite devem ficar em um volume privado autorizado, com backups e controle de acesso. Arquivos sintéticos do CI **não são** modelo homologado. Execute a inicialização do MCE, com modelo `.xlsx` não alterado e todas as exportações incluídas no inventário SHA-256:

```powershell
python .\systems\mce\.agents\skills\engenharia-mce-projeto\scripts\mce_workflow.py init --workspace "C:\MCE_DADOS\PROJETO_MCE" --master "C:\MCE_FONTES\MODELO_MESTRE.xlsx" --sources "C:\MCE_FONTES\pid.json" "C:\MCE_FONTES\ocr.csv" "C:\MCE_FONTES\exemplo.json" "C:\MCE_FONTES\io.csv"
python .\systems\mce\scripts\mce_memory.py --db "C:\MCE_DADOS\mce.sqlite3" init
```

Inicializar não aprova o modelo: a classificação padrão é `MODELO_FORNECIDO_NAO_VERIFICADO` e o contrato inicial bloqueia todas as células.

## 2. Criar o manifesto por execução (fora do repo)

```json
{
  "schema": "mce.matriz-tool.manifest.v1",
  "run_id": "LEVANTAMENTO_001",
  "sources": [
    {"adapter": "azure", "source_name": "pid.json", "document": "PI-001", "revision": "R00", "location": "folha 1"},
    {"adapter": "houston", "source_name": "ocr.csv", "document": "PI-001", "revision": "R00", "location": "folha 1"},
    {"adapter": "industrial", "source_name": "exemplo.json", "document": "EXEMPLO-DIDATICO", "revision": "REF", "location": "benchmark sem validade de projeto"}
  ],
  "io_source_name": "io.csv"
}
```

Todos os arquivos devem estar no inventário. O terceiro adaptador é **facultativo** em projeto real: se ausente, o DataSheet o registra em `missing_adapters`, sem inventar evidência. Um ou dois adaptadores também podem ser processados. O I/O opcional só pode ser comparado com o grafo Azure; sem correspondência textual não é inferida lógica funcional.

## 3. Planejar, executar e auditar

```powershell
python .\systems\mce\scripts\matriz_causa_efeito_tool.py plan --workspace "C:\MCE_DADOS\PROJETO_MCE" --manifest "C:\MCE_DADOS\manifest.json" --db "C:\MCE_DADOS\mce.sqlite3"
python .\systems\mce\scripts\matriz_causa_efeito_tool.py run --workspace "C:\MCE_DADOS\PROJETO_MCE" --manifest "C:\MCE_DADOS\manifest.json" --db "C:\MCE_DADOS\mce.sqlite3"
python .\systems\mce\scripts\mce_memory.py --db "C:\MCE_DADOS\mce.sqlite3" verify
python .\systems\mce\scripts\mce_memory.py --db "C:\MCE_DADOS\mce.sqlite3" search --text MCE_TOOL_MATRIZ_CAUSA_EFEITO
```

`plan` **não grava** estado; `run` pré-valida todos os formatos, exige SQLite existente/verificado e depois usa `scripts/mce_system.py pid-import` e `compare-io` para criar derivados registrados em `state.json`. O DataSheet é `workspace/derived/MCE_<run_id>_DATASHEET.json`, validável contra `datacenter/MATRIZ_CAUSA_EFEITO_DATASHEET.schema.json`. Contém hashes, referência do repositório, contagem de observações e estado **pendente de revisão**, sem texto OCR/TAGs ou lógica automática. Um evento `STATUS` com `tool=matriz-causa-efeito` é anexado **ao DataCenter MCE existente**, com SHA-256 do DataSheet; o JSON DataSheet não é publicado em GitHub.

Nenhuma reexecução sobrescreve arquivos. Se a operação falhar após começar a registrar derivados, conservar os arquivos para auditoria e **usar novo run_id e workspace revisado**, sem apagar ou forçar avanço; não há transação distribuída entre arquivos e banco. O DataSheet registra fase canônica `INVENTARIADO` e estado da ferramenta `PRE_ANALISE_PENDENTE_REVISAO`, não finge que o relatório de entendimento já foi aprovado.

## 4. Fechamento da pré-análise e gate humano

O engenheiro deve conferir os derivados, fontes literais, revisões e hashes; compor `analise.json` e uma entrada `pid_integration_review[]` para **cada** artefato derivado com revisão humana explícita. Só então usar `mce_workflow.py understand`, que termina em **`ANALISADO_AGUARDANDO_DECISAO`**. Só depois da autorização externa `AUTORIZO_ELABORACAO_MCE`, modelo mestre e contrato de células aprovados, acionar `authorize`, `apply` e `audit` no *executor anterior* com cópia do XLSX. Limite 50 causas/folha; cinza D9D9D9 apenas em texto alterado; preservar OOXML e revisão FAT/SAT aplicável.

### Limites e gates

- A CI testa dados sintéticos nos três formatos **exclusivamente em Windows**. Os testes não aprovam intertravamentos nem executam o host Codex/ChatGPT Web.
- Banco, documentos, modelos, DataSheets completos, backups e transcrições privadas **não** entram no GitHub público.
- O histórico de decisões públicas fica no Issue #120 e `spec/memoria.md`; eventos operacionais privados ficam no banco MCE.
- `PRODUCTION_COMPLETE=NO` até segurança, revisão humana, host, release, modelo mestre e aceite comprovados.

## Plataforma única Windows

A ferramenta só pode ser criada, desenvolvida, testada e operada em **Windows nativo**, com PowerShell 7 e Python 3.12+. Não usar Linux, WSL, Bash ou contêiner Linux. Os caminhos `C:\MCE_DADOS` e `C:\MCE_FONTES` são exemplos de pastas privadas já existentes, fora do checkout GitHub.

A CI `.github/workflows/mce-matriz-tool-qa.yml` executa apenas `windows-latest`, testa os três adaptadores sintéticos, valida todos os espelhos das Skills e gera `dist/skill.zip` usando `Compress-Archive`. O ZIP fica no artefato `matriz-causa-efeito-windows-skill`. Os checks globais compartilhados não são modificados por esta decisão MCE.
