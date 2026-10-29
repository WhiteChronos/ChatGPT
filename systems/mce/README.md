# Sistema MCE INDEPENDENTE — Matriz de Causa e Efeito

**Sistema próprio de engenharia industrial; não depende de REA, MCP ou serviços Web externos.**

Contém duas Skills locais `padronizacao-mce` e `engenharia-mce-projeto`, editor OOXML de texto controlado, inventário SHA-256, prévia P&ID via adaptadores de formato JSON/CSV, verificação humana e testes.

## Instalar e verificar

Requer Python 3.12+; no diretório extraído:

```bash
python -m pip install -r requirements.txt
python scripts/validate_skills.py
python -m pytest -q tests/
```

No Codex, colocar ambas as pastas sob `.agents/skills/` do projeto MCE e iniciar sessão nova, verificando a descoberta. No ChatGPT Web, importar as Skills individualmente quando a interface da conta oferecer a opção. A presença dos arquivos no pacote não confirma instalação global.

## Fase 1 (não editar Excel)

```bash
python .agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py init --workspace PROJETO --master MODELO.xlsx --sources P_ID.pdf lista-io.csv
python .agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py understand --workspace PROJETO --analysis analise.json
```

Prepare `analise.json` com evidências literais e revise as fontes; consulte `docs/EXECUCAO.md` antes da análise. O fluxo **para** em `ANALISADO_AGUARDANDO_DECISAO`.

### P&ID/IO opcional e local

```bash
python scripts/mce_system.py pid-import --workspace PROJETO --adapter azure --source-name grafo.json --document PI-001 --revision R00 --location 'folha 1'
python scripts/mce_system.py compare-io --workspace PROJETO --graph-name PID_NORMALIZADO.json --io-name lista-io.csv
```

As saídas são candidatas, precisam estar no inventário inicial e requerem revisão humana registrada por SHA. Não são propostas de intertravamento aprovadas.

## Fase 2: somente após autorização formal

```bash
python .agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py authorize --workspace PROJETO --authorization autorizacao.json
python .agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py apply --workspace PROJETO --changes alteracoes.json
python .agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py audit --workspace PROJETO
```

O executor modifica uma cópia do modelo `.xlsx` somente em células textuais explicitamente liberadas, destaca em cinza e audita os demais componentes OOXML. Não oferece autorização automática, homologação Petrobras nem suporte `.xlsm` neste fluxo.

## Independência

- Executável principal: `scripts/mce_system.py`, `mce_workflow.py` nas Skills.
- Código de P&ID: `pid_bridge.py` na Skill de engenharia; **sem dependência REA ou MCP**.
- Pacote separado de qualquer motor de engenharia reversa, porta HTTP ou biblioteca de varredura de código.
- Fontes GitHub catalogadas em `research/` são referências metodológicas, sem execução de código de terceiros.

## Preparacao para producao (nao homologacao automatica)

Ver `docs/PRODUCTION_ACCEPTANCE.md` para a lista de evidencias obrigatorias e verificacao fail-closed. Exemplo de comando: `python scripts/production_readiness.py --workspace /PROJETO_MCE_AUTORIZADO`. O resultado automatico nao certifica `PRODUCTION_COMPLETE`.

## Novo gate de integridade do pacote independente

Antes de instalar qualquer release MCE, executar `python scripts/release_integrity.py --zip /RELEASE_APROVADO.zip` e conferir `INTEGRITY_PASS`, incluindo verificacao SHA-256 de todos os membros. Consulte `docs/RELEASE_INTEGRITY.md`. Esse gate **nao** dispensa autorizacao documental, verificacao do workbook mestre, revisao e aceite de engenharia. Nenhuma dependencia com REA foi adicionada.

### Verificacao adicional de procedencia

Para um candidato aprovado, informe tambem `--expected-sha256 SHA256_DO_CANAL_CONFIAVEL` e `--expected-git-sha COMMIT40_REVISADO`. Consulte `docs/RELEASE_INTEGRITY.md`: hashes internos nao comprovam origem, e nenhuma flag comprova engenharia ou producao automaticamente.


## Skill adicional: fechamento operacional (2026-10-29)

A Skill `.agents/skills/mce-fechamento-operacional/` organiza a comprovacao tecnica sem escrever no Excel mestre, com verificador de SHA-256 de evidencias e bloqueio explicito de homologacao automatica. As Skills originais de elaboracao MCE e padronizacao do modelo permanecem independentes e intocadas.

O operador deve obter modelo oficial, projeto/SS, documentacao e aceite externo. O verificador de arquivos retorna `ARTIFACT_INTEGRITY_PASS` apenas para correspondencia de hashes, **nao** `PRODUCTION_COMPLETE`.

## DataCenter SQL e memoria persistente independente (29/10/2026)

A memoria operacional SQLite versionada, DataSheet, busca de registros, backup/restauracao, verificador de integridade e pipeline read-only estao em `docs/DATACENTER_MEMORY.md`. Os bancos reais pertencem ao host privado, nunca ao GitHub ou ao ChatGPT. CI de seguranca e testes: `.github/workflows/mce-memory-qa.yml`. `PRODUCTION_COMPLETE=NO` ate ambiente real, revisao e aceite independentes.
 
## Retomada de contexto em nova conversa

**Memória documental canônica deste produto:** [`spec/memoria.md`](spec/memoria.md). Antes de continuar trabalho no Codex ou ChatGPT Web, consultar este arquivo, `AGENTS.md`, `docs/DATACENTER_MEMORY.md` e o HEAD/CI reais do [PR #118](https://github.com/WhiteChronos/ChatGPT/pull/118). Não reconstruir etapas já comprovadas; decisões e pendências têm IDs estáveis. A memória não recolhe chats automaticamente; acrescentar novos fatos apenas após verificação e sem publicar conteúdo confidencial.


## Memoria GitHub sem dependencia do ChatGPT

Indice permanente: https://github.com/WhiteChronos/ChatGPT/issues/120. Memoria canonica: [spec/memoria.md](spec/memoria.md). Contrato: [docs/GITHUB_MEMORY.md](docs/GITHUB_MEMORY.md). CI: .github/workflows/mce-github-memory.yml. Para atualizar o sistema, adicionar registro datado da decisao no mesmo commit. Nao ha captura automatica dos chats.


## Captura imediata de decisoes

O Issue #120 e uma caixa de entrada persistente: https://github.com/WhiteChronos/ChatGPT/issues/120 . Consulte scripts/github_memory_inbox.py para eventos ainda nao consolidados no spec/memoria.md. A CI audita todo o historico recente. O ChatGPT nao oferece captura nativa automatica de cada mensagem no GitHub.


## Skill Matriz de Causa e Efeito — entrada MCE exclusiva

A nova [`matriz-causa-efeito`](.agents/skills/matriz-causa-efeito/SKILL.md) e o ponto de entrada especializado para elaborar e revisar MCE a partir de P&IDs, lista I/O, narrativas e modelo mestre. Coordena as 3 Skills existentes, usa catalogo GitHub auxiliar revisado, nao duplica a edicao OOXML e para em `ANALISADO_AGUARDANDO_DECISAO`. So edita copia derivada com modelo oficial, contrato e `AUTORIZO_ELABORACAO_MCE` comprovados. Instalacao no ChatGPT Web e Codex precisa ser feita/verificada na plataforma correspondente.
