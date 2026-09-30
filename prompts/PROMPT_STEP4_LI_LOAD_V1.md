# PROMPT - PASSO 4 - LI E CARGA POR PAINEL - V1

ID: PROMPT-STEP4-LI-LOAD-V1
STATUS: MANDATORY_CONTROLLED
PRE-REQUISITOS: STEP1_SCOPE_FROZEN + STEP2_PANEL_DEFINITION_FROZEN + STEP3_NORMATIVE_ACADEMIC_BASE_FROZEN

## OBJETIVO

Criar a Lista de Materiais e a Carga de cada painel do projeto, com quantitativos rastreaveis e calculados a partir da engenharia real.

A saida deste passo e somente um workbook de LI/Carga.

## ESTRUTURA DO WORKBOOK

Para cada PANEL_ID criar exatamente duas abas:
- <PANEL_ID>_MATERIAIS
- <PANEL_ID>_CARGA

Para N paineis devem existir exatamente 2N abas.

Proibido no workbook final:
- capa;
- controle;
- referencias separadas;
- arquitetura;
- QA;
- memoria;
- abas ocultas;
- qualquer terceira aba por painel.

Toda rastreabilidade deve aparecer em colunas das duas abas permitidas ou no Data Center.

## ABA MATERIAIS

Incluir tudo que for fisicamente usado:
- gabinete, placa e acessorios;
- PLC, I/O, switch, gateways, IHM e comunicacao;
- fontes, UPS, baterias, conversores;
- disjuntores, fusíveis, porta-fusiveis, DPS e acessorios;
- relés, interfaces, contatores e soquetes;
- bornes, PE, blindagem, jumpers, pontes, separadores, end stops;
- trilho DIN e acessorios;
- canaletas, tampas e fittings;
- fios internos por tipo/secao/cor/metragem calculada;
- condutor PE, equipotencializacao e tranca de porta;
- cabos internos Ethernet/fieldbus e conectores;
- ilhoses, terminais, olhais, garfos, heat-shrink e marcadores;
- prensa-cabos, tampoes e passagens;
- climatizacao e kits;
- parafusos, porcas, arruelas, espacadores e suportes;
- qualquer kit exigido pelo fabricante.

Cada linha deve ter quantidade, unidade, metodo de calculo, REF_ID e links oficiais.

## ABA CARGA

Uma aba por PN.

Cada carga deve registrar:
- tag;
- fabricante/modelo;
- quantidade;
- tensao;
- corrente/potencia nominal;
- duty/diversity somente quando documentado;
- carga bruta;
- carga de projeto;
- criticidade UPS;
- perda termica quando disponivel;
- REF_ID e link oficial.

## QUANTIFICACAO MATEMATICA

### Fiacao interna

Antes de calcular metros:
1. criar grafo de conexoes;
2. definir origem/destino de cada condutor;
3. definir rota fisica aprovada;
4. medir a rota em mm no layout real;
5. somar terminacoes e service loop;
6. aplicar margem de fabricacao somente se for parametro explicito do projeto.

Formula:
L_corte = L_rota + L_terminal_origem + L_terminal_destino + L_service_loop

Quantidade de compra:
L_compra = L_corte x (1 + margem_fabricacao_parametrizada)

Nao usar distancia reta se o fio passa por canaletas.

### Materiais lineares

Calcular por geometria:
- trilho DIN;
- canaleta e tampa;
- cabo de rede/bus;
- PE/equipotencializacao;
- fios internos.

### Bornes e terminacoes

Derivar do grafo de conexoes e do plano de bornes.

Contar separadamente:
- borne normal;
- borne PE;
- borne de blindagem;
- jumper/ponte;
- end plate;
- end stop;
- marcador;
- ilhos/terminal de cada ponta.

### Canaletas

Dimensionar comprimento pela rota fisica e ocupacao pela area dos condutores, respeitando fabricante/norma aplicavel.

Volume do gabinete e area da placa servem como verificacao, mas nao substituem colisao, folga, acesso e manutencao.

## FERRAMENTAS

Usar:
- Wolfram para comprimento, area, volume, ocupacao e carga;
- QElectroTech para esquemas e conexoes;
- WireViz/QetWireManager para listas de fios/conexoes quando validados;
- NetworkX para validar grafo;
- OR-Tools para otimizar rotas quando aplicavel;
- FreeCAD/CadQuery/build123d/OpenCascade para layout e medicao real;
- Remote Desktop Commander para operar ferramentas locais autorizadas;
- B&A Diagrams/tldraw/Miro apenas para revisao/visualizacao;
- Tavily/Firecrawl para fabricante e fornecedor;
- Scite/Consensus para suporte academico.

Ferramenta grafica nunca e autoridade de quantidade por si so.

## FORNECEDORES E LINKS

Prioridade:
1. fabricante oficial;
2. portal tecnico oficial;
3. distribuidor autorizado;
4. representante oficial.

Cada item deve ter link oficial e, quando possivel, link de fornecedor autorizado.

## MONTAGEM DE QUADROS

Usar:
- manual de instalacao do fabricante;
- manual de acessorios;
- catalogo dimensional;
- treinamento oficial;
- normas;
- literatura tecnica;
- estudos academicos;
- videos oficiais ou tecnicos como evidencia secundaria.

Video de montagem nao define corrente nominal, Icu, IP, secao de cabo ou requisito normativo.

## QA

Bloquear quando:
- quantidade sem base;
- metragem sem grafo e rota;
- acessorio obrigatorio ausente;
- link/modelo divergente;
- item energizado na LI ausente da carga sem justificativa;
- revisoes divergentes;
- geometria desatualizada;
- workbook tiver abas extras.

## SAIDA

LI_LOAD_WORKBOOK
MATERIAL_QUANTITY_TRACE
INTERNAL_WIRE_CUTLIST
LOAD_CALCULATION_TRACE

Gate:
STEP4_LI_LOAD_FROZEN

Regra:
A LI E A CARGA DEVEM SER CALCULADAS A PARTIR DO PAINEL QUE SERA MONTADO, NAO ESTIMADAS A PARTIR DE UMA IMAGEM.
