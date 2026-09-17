# PROMPT-MASTER-LI-MATERIAL-V1

**Status:** LOCKED_APPROVED_STANDARD  
**Escopo:** criação, revisão, validação e emissão de LI – Lista de Material em XLSX.  
**Mudança:** somente mediante autorização explícita do responsável do projeto.

## 1. Regra central
Ao revisar uma LI existente, nunca sobrescrever a coluna de uma revisão anterior. A revisão anterior permanece exatamente como foi emitida. A nova revisão deve ser criada na coluna imediatamente à direita da última revisão existente.

Exemplo obrigatório:

`REV. 0 | REV. A | REV. B | ...`

Se a planilha possuir `REV. 0` e o projeto estiver emitindo `REV. A`, todos os valores históricos de `REV. 0` ficam imutáveis e todos os quantitativos corrigidos entram somente em `REV. A`.

## 2. Fontes permitidas para o quantitativo da nova revisão
Usar somente evidência rastreável, na seguinte ordem operacional:

1. desenho/projeto oficial vigente;
2. desenho do painel aprovado pelo responsável do projeto;
3. workbook/planilha de referência aprovada pelo responsável do projeto;
4. Data Center e Data Sheet vigentes;
5. documentação oficial do fabricante;
6. cálculo determinístico derivado das fontes acima.

Nunca copiar automaticamente o valor da revisão antiga apenas para preencher a nova. Nunca inferir quantidade sem evidência. Quando duas fontes autorizadas divergirem, manter a revisão anterior intocada e marcar a nova revisão como `HOLD` até reconciliação.

## 3. Regra para A LEVANTAR
`A LEVANTAR` somente é permitido quando a quantidade não puder ser determinada de forma objetiva a partir das fontes vigentes. Cada `A LEVANTAR` deve possuir motivo e referência da lacuna.

Se o quantitativo puder ser contado ou calculado a partir do desenho do painel, projeto, lista de referência ou Data Sheet, ele deve ser preenchido na nova revisão.

## 4. Preservação do workbook
Preservar sem alteração não autorizada:
- capa;
- identidade gráfica;
- ordem das folhas;
- nomes das folhas;
- mesclagens;
- larguras de coluna;
- alturas estruturais de linha;
- cabeçalhos e rodapés;
- área de impressão;
- orientação e configuração de página;
- revisões anteriores;
- fórmulas fora do escopo autorizado.

Uma correção de conteúdo não autoriza reconstruir o template.

## 5. Fluxo obrigatório
`BASELINE → IDENTIFICAR REVISÕES → CONGELAR REVISÕES ANTERIORES → LEVANTAR FONTES → DETERMINAR QUANTIDADES → PREENCHER NOVA REVISÃO → QA ESTRUTURAL → QA SEMÂNTICO → REGISTRAR MEMÓRIA → EMISSÃO`

## 6. QA obrigatório
Antes de emitir, verificar:
- revisão anterior byte/célula logicamente preservada;
- nova revisão na coluna correta;
- nenhuma célula histórica alterada;
- quantidade nova rastreável;
- `A LEVANTAR` justificado;
- capa e formato preservados;
- planilha abre como OOXML válido;
- áreas de impressão preservadas;
- workbook sem links externos novos inesperados;
- diff semântico revisado.

## 7. Open source QA
Quando disponível no ambiente, usar em camadas:
- `openpyxl`: leitura/edição conservadora e inspeção estrutural;
- `lxml`: validação XML/OOXML;
- `WorkbookLens`: lint, diff semântico, regressão e reparo conservador de XLSX;
- `SheetParity`: recálculo e comparação em motor real de planilha, preferencialmente LibreOffice em CI;
- `LibreOffice`: abertura/renderização/recálculo headless para verificação complementar;
- `Pillow`: comparação visual de renderizações;
- `pytest`: testes de regressão;
- `pre-commit`: gate local antes de commit.

Ferramentas externas não podem auto-instalar nem alterar o workbook sem revisão. A ausência de ferramenta opcional deve ser registrada como cobertura de QA reduzida, não mascarada como PASS total.

## 8. Memória de controle
Cada alteração de LI deve gerar um registro com:
- data/hora;
- documento lógico;
- revisão anterior;
- nova revisão;
- folhas alteradas;
- colunas de revisão;
- fontes usadas;
- itens alterados;
- itens mantidos `A LEVANTAR`;
- conflitos/HOLDs;
- resultado do QA;
- hash/snapshot quando disponível.

A memória registra o histórico, mas nunca substitui os documentos oficiais ou as revisões gravadas na planilha.

## 9. Status
- `VALIDADO`: evidência suficiente, histórico preservado e QA aprovado.
- `HOLD`: quantidade, fonte ou conflito ainda pendente.
- `REPROVADO`: revisão histórica alterada, template modificado sem autorização, coluna de revisão incorreta ou dado inventado.
