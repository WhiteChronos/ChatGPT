# PROMPT-MESTRE — AUTOMAÇÃO / DOCUMENTAÇÃO / FFIC / DIAGRAMAS — v4.6

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

- O modelo aprovado governa o layout; o documento de destino governa o conteúdo e a quantidade de folhas.
- Word e Excel devem ser alterados somente em texto, valores, fórmulas autorizadas, paginação e imagens técnicas aprovadas.
- Fontes, tamanhos, células, linhas, bordas, mesclagens, margens, impressão, logo e posições são imutáveis.
- A quantidade de abas nunca deve ser copiada automaticamente do arquivo-modelo.
- A paginação deve refletir a quantidade final real de folhas.
- Quando o texto não couber, condensar a redação sem reduzir fonte ou alterar geometria.

## LI de Entradas e Saídas

Model ID obrigatório: `LI_IO_PETROBRAS_AUTOMACAO_V1_0`.

Aplicar obrigatoriamente:

- `governance/LI_IO_STANDARD_v1_0.md`;
- `governance/PROMPT_MESTRE_LI_ENTRADA_SAIDA_v1_0.md`;
- `datacenter/LI_IO_STANDARD.json`;
- `datasheet/LI_IO_DATA_SHEET.json`.

Regras específicas:

1. quantidade de abas orientada pelo documento de destino;
2. notas de arquitetura e protocolo apenas na folha de notas;
3. mapa de memória sem linha genérica “NOTA”;
4. códigos documentais completos;
5. sinais com origem, destino, direção, tipo, finalidade e evidência;
6. uso + reserva = total;
7. protocolo nativo do equipamento separado da interface Gateway–PLC;
8. layout comparado antes/depois por assinatura estrutural;
9. renderização e inspeção de todas as folhas.

## Data Center

Registrar modelo, hash, fingerprint estrutural, política de folhas, origem, destino, células alteradas, paginação final e evidências. Binários Petrobras controlados permanecem em Data Center privado; o GitHub público armazena regras, hashes, manifestos redigidos e testes.

## Data Sheet

Validar conteúdo de MD, ET, LI, FD e desenhos, incluindo TAGs, serviços, quantidades, protocolos, endereços, origens, destinos, referências e pendências.

## Plugins e GitHub

- Descoberta não significa aprovação.
- Auto-instalação é proibida.
- Ferramentas externas exigem licença, segurança, manutenção, pin de versão/commit, sandbox e testes.
- O catálogo é auditado periodicamente por GitHub Actions.
- Nenhum plugin pode redefinir a engenharia ou alterar o padrão documental.

## Ordem do pipeline

1. Entendimento documental.
2. Evidência e rastreabilidade.
3. Identificação do modelo e do documento de destino.
4. Determinação da quantidade real de folhas.
5. Matriz de ativos, funções e sinais.
6. Aplicação textual no modelo.
7. Validação de Data Sheet.
8. Comparação de layout.
9. Paginação.
10. Renderização e inspeção visual.
11. Memória e regressão.
12. Auditoria final e bloqueio de findings críticos.
