# PROMPT-MESTRE — AUTOMAÇÃO / DOCUMENTAÇÃO / FFIC / DIAGRAMAS — v4.7

## Regra de ouro de engenharia

- Nunca sair da simbologia AUTOMAÇÃO DM R00-05.
- Todos os símbolos funcionais devem ter envoltória externa nominal de 12 mm.
- O símbolo nunca pode ser achatado, alongado ou redimensionado para acomodar texto.
- CMD, RUN, FAULT e AVAILABLE são informações independentes.
- MAN/AUTO não é equivalente a LOCAL/REMOTO.
- Nenhuma linha ou sinal pode ser órfão.
- Intertravamentos exigem causa, condição, equipamento afetado, efeito, feedback, reset, estado seguro e fonte.
- Alarme não implica trip.
- Informação sem evidência permanece TBD/PROPOSTO.

## Regra de ouro documental

- O modelo aprovado governa o padrão visual; o documento de destino governa o conteúdo e a quantidade real de folhas.
- Em revisão de Word/Excel existente, o próprio arquivo recebido é a matriz física.
- Alterar somente texto, valores técnicos, paginação autorizada e imagens técnicas explicitamente aprovadas.
- Não alterar espaçamento de parágrafo, espaçamento entre linhas, recuos, tabs, alinhamentos, fontes, tamanhos, tabelas, células, bordas, mesclagens, margens, headers, footers, logos, seções ou geometria.
- Quando o texto não couber, condensar a redação tecnicamente; nunca comprimir o layout.
- Paginação e referências de página devem refletir a emissão final real.

## MD — Memorial Descritivo de Automação

Model ID obrigatório: `MD_AUTOMATION_PETROBRAS_V1_0`.

Aplicar:

- `governance/MD_AUTOMATION_STANDARD_v1_0.md`;
- `governance/PROMPT_MESTRE_MD_AUTOMACAO_v1_0.md`;
- `datacenter/MD_AUTOMATION_STANDARD.json`;
- `datasheet/MD_AUTOMATION_DATA_SHEET.json`;
- `pipeline/md_revision_standard.py`.

Regras específicas da revisão de MD:

1. o espaçamento e toda a apresentação do modelo/matriz são imutáveis;
2. antes da revisão corrente, remover todo cinza D9D9D9 herdado de revisões anteriores;
3. o mapa de mudanças da revisão corrente é a fonte de verdade — nunca o cinza legado;
4. aplicar D9D9D9 apenas ao texto efetivamente alterado na revisão corrente;
5. o cinza deve ser visualmente contínuo em todos os runs textuais do bloco revisado, inclusive espaços existentes entre palavras;
6. é proibido inserir espaços, tabs ou quebras para preencher cinza;
7. índice/sumário deve marcar títulos e páginas afetados pela revisão corrente;
8. renderizar e inspecionar todas as páginas a 100%;
9. qualquer mutação de spacing/pPr, fonte, tabela, seção, header/footer ou geometria bloqueia a emissão.

## LI de Entradas e Saídas

Model ID obrigatório: `LI_IO_PETROBRAS_AUTOMACAO_V1_0`.
Aplicar `governance/LI_IO_STANDARD_v1_0.md`, `governance/PROMPT_MESTRE_LI_ENTRADA_SAIDA_v1_0.md`, `datacenter/LI_IO_STANDARD.json` e `datasheet/LI_IO_DATA_SHEET.json`.
A quantidade de abas vem do documento de destino e não do modelo visual.

## Compatibilização técnica — modelo obrigatório

Model ID: `AUTOMATION_COMPATIBILITY_REPORT_MODEL_V1_0`.

Aplicar em toda análise de compatibilidade, auditoria, reavaliação ou parecer de Automação:
- `governance/AUTOMATION_COMPATIBILITY_REPORT_MODEL_v1_0.md`;
- `governance/AUTOMATION_HYPERFOCUS_GOLDEN_RULE_v1_0.md`;
- `datacenter/AUTOMATION_COMPATIBILITY_REPORT_MODEL.json`;
- `datacenter/AUTOMATION_REFERENCE_LIBRARY.json`;
- `datasheet/ENGINEERING_COMPATIBILITY_DATA_SHEET.json`;
- `pipeline/engineering_compatibility_gate.py`;
- `pipeline/protocol_zero_gate.py`.

Regras obrigatórias:
1. /visualize é o padrão; Build Web Data Visualization é aprimoramento quando disponível;
2. dúvida vem antes de finding;
3. antes de perguntar ao usuário, pesquisar baseline do projeto e fontes normativas/oficiais aplicáveis;
4. pergunta aberta deve registrar `source_checks` e campo de resposta;
5. erro confirmado deve listar documentos envolvidos e critério de fechamento;
6. norma/referência deve registrar aplicabilidade; `REFERENCE_ONLY` não cria não conformidade sozinha;
7. documento revisado precisa ser rechecado antes de encerrar finding ou liberar o projeto.

## Pesquisa técnica antes de afirmar associação
Aplicar `AUTOMATION_EVIDENCE_RESEARCH_GOLDEN_RULE_v1_0`.

Nunca associar DO, DI, AI, AO, relé, contato, borne, cabo, gateway, switch ou outro objeto por quantidade, nome, prefixo de TAG ou proximidade documental sem evidência explícita.

Caso a relação seja ambígua:
- pesquisar a baseline do projeto;
- consultar normas/fontes oficiais;
- consultar fabricante;
- procurar literatura técnica aberta;
- pesquisar GitHub/repositórios open source;
- usar plugins/conectores de pesquisa para descobrir fontes;
- distinguir claramente conceito geral de evidência específica do projeto.

Regra permanente: DO é um ponto/canal de saída do controlador; relé externo é dispositivo separado e só pode ser associado ao DO quando o projeto demonstra a ligação.

## Perguntas ao usuário — formato obrigatório

Em compatibilização de Automação, não gerar lote de perguntas em lista Markdown quando houver superfície `/visualize` interativa disponível.

Toda pergunta deve aparecer em card com:
- ID;
- criticidade/prioridade;
- área/disciplina;
- pergunta objetiva;
- motivo da pergunta;
- documentos envolvidos;
- checagens já realizadas;
- status Protocol Zero;
- campo de resposta;
- mecanismo para gerar/copiar bloco de respostas.

Perguntas respondidas permanecem auditáveis em “Perguntas Resolvidas”. Pergunta sem resposta permanece NOT_VERIFIABLE e nunca vira erro automaticamente.

## Data Center e Data Sheet

Registrar modelo, hash, fingerprint estrutural, documento de destino, alterações autorizadas, paginação final, mapa de revisão, evidências técnicas e evidências de renderização. Binários Petrobras permanecem em armazenamento privado controlado; o GitHub armazena apenas regras, hashes, fingerprints, esquemas e testes.

## Plugins e GitHub

- Descoberta não significa aprovação.
- Auto-instalação é proibida.
- Ferramentas externas exigem licença, segurança, manutenção, pin de versão/commit, sandbox e testes.
- Nenhum plugin pode redefinir a engenharia nem alterar o padrão documental.

## Ordem do pipeline

1. Entendimento documental.
2. Evidência e rastreabilidade.
3. Identificação do modelo e da matriz física.
4. Captura do fingerprint estrutural.
5. Limpeza da marcação de revisão anterior, quando aplicável.
6. Aplicação textual cirúrgica.
7. Marcação exclusiva da revisão corrente.
8. Validação Data Sheet e coerência MD/ET/LI/FD/DE.
9. Comparação estrutural antes/depois.
10. Paginação e índice.
11. Renderização e inspeção visual integral.
12. Memória, regressão e bloqueio de findings críticos.
