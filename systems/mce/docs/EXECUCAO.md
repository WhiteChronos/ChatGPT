# Contratos de entrada, saida e autorizacao

## `analise.json` (fase A)
Campos obrigatorios: `project`, `ss`, `summary`, `findings`, `gaps`. Cada `findings[]` com classificacao `DOCUMENTADO` deve conter `text`, `source_name`, `line` (para .txt/.md) e `verbatim_excerpt`; a fonte registrada deve ser identificavel no inventario. Se projeto/SS nao forem `NAO IDENTIFICADO`, exigir `identity_evidence` para ambos, contendo fontes, linhas e trechos literais. Para PDF/DOCX/XLSX, necessaria verificacao manual do trecho, revisao, pagina/desenho e TAG; a sinalizacao `manual_evidence_verified` representa declaracao do revisor, nao prova automatizada.

## `contract.json` (Skill 01)
Criado com tudo bloqueado. Liberar `model_approved=true` apenas para o template efetivamente aprovado. Registrar `protected_rows_by_sheet` para todas as abas, `frozen_sheets`, `matrix_ranges` e as coordenadas exatas em `editable_cells`; o inventario inicial precisa ter `template_classification=MODELO_APROVADO`. `max_causes_per_sheet` deve permanecer 50. Antes de aprovar, revisar cabecalhos, legendas, notas fixas, protecao, formulas, mesclas, estilos condicionais e areas de impressao. A ferramenta rejeita intervalos que excedam as linhas existentes no modelo.

## `autorizacao.json` (gate humano)
Exemplo de formato (dados de demonstracao):

```json
{
  "decision": "AUTORIZO_ELABORACAO_MCE",
  "approver": "RESPONSAVEL PELA APROVACAO",
  "project": "DENOMINACAO DOCUMENTADA",
  "ss": "SS DOCUMENTADA",
  "source_manifest_sha256": "HASH DO INVENTARIO"
}
```

A autorizacao e guardada no `state.json`, vinculada ao inventario de fontes. Nao usar este arquivo de exemplo para representar aprovacao real: o agente so deve criar este registro depois da manifestacao expressa do responsavel.

## `alteracoes.json` (fase B)
Lista de edicoes **textuais** com `sheet`, `cell`, `old_text`, `new_text`, `source_name`, `source_sha256`, `source_location`, `reference_revision`, `verbatim_excerpt` e `evidence_status=DOCUMENTADO`. Sem fonte, sem alteracao. Nenhuma edicao e inferida automaticamente do grafo do P&ID.

## Saidas
- `base/modelo.xlsx` preservada por SHA-256.
- `sources/`: copias locais das fontes informadas.
- `state.json`: historico de fases e digests do modelo/documentos.
- `RELATORIO_ENTENDIMENTO.md`: relatorio fundamentado com STOP.
- `output/MCE_PRELIMINAR.xlsx`: apenas quando TODOS os gates forem satisfeitos.
- `ALTERACOES_MCE.json` e `AUDITORIA_MCE.json`: diff e QA detalhados.

## Erros impeditivos e limites
A falta de Projeto/SS, ausência de original oficial, liberação de celula de cabecalho, fonte divergente, mais de 50 causas por folha, alteracao em formula, cores funcionais, alteracao nao autorizada ou falha no audit bloqueiam a saida. O QA automatizado comprova invariantes estruturais analisadas e nao garante sozinho equivalencia visual de recursos Excel exóticos ou validade de uma SIF. Exigir revisao humana e FAT/SAT para aceite operacional.

## Pesquisa GitHub de P&ID

A extensao usa `scripts/mce_system.py` para orquestrar `pid_bridge.py` sem modificar `mce_workflow.py` no que se refere aos gates de autorizacao de MCE. Depois do inventario e antes do relatorio de entendimento, registrar as exportacoes de P&ID como fontes no init. Importar com `pid-import`, comparar com lista I/O com `compare-io` e exigir `pid_integration_review` para cada SHA derivado. Nao executar o modelo de terceiros; somente converter JSON/CSV entregue pelo usuario. Ver `README.md` e `research/top10_verificados.json`.

**Falha de seguranca detectada:** o exemplo didatico Industrial-Control tem sombreamento de parametro em `validate_coverage`, impedindo reconhecer efeitos ausentes; foi reimplementado em validador proprio com teste adversarial. **Licencas:** S-Houston e Industrial-Control sem licenca identificada; pyDEXPI AGPL-3.0 (nao incorporado). Nenhum dado de projeto publicado.
