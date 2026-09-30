# DIRETRIZ MESTRA DE ELABORAÇÃO DE IMAGEM DE PAINEL PN — V1

**ID:** PROMPT-DIRETRIZ-IMAGEM-PN-V1  
**Status:** MANDATORY / CONTROLLED  
**Modelo visual base:** PN-IMAGE-MODEL-001  
**Aplicação:** qualquer painel PN novo ou revisão de imagem de painel PN existente  
**Autoridade:** esta diretriz governa o PROCESSO DE ELABORAÇÃO DA IMAGEM; não substitui Data Sheet, LI/BOM, cálculos, normas ou documentação oficial de fabricante.

---

## 0. Divisão obrigatória em Passo 5 e Passo 6

A elaboração visual foi dividida em duas etapas independentes e sequenciais:

**Passo 5 — imagem física do PN**
- um PANEL_ID por conjunto;
- uma montagem 3D canônica;
- mesma porta/tampa em todos os ângulos;
- somente câmera e rotação rígida no eixo de dobradiça podem mudar;
- sem legenda, arquiteturas, comando ou bloco documental final;
- saída: STEP5_PN_IMAGE_FIDELITY_FROZEN.

**Passo 6 — documento visual de engenharia**
- reutiliza a imagem/fingerprint congelado do Passo 5;
- adiciona legenda, dados, arquitetura elétrica, arquitetura de comunicação, diagrama de comando e dimensionamento;
- não altera geometria;
- canvas cresce e vistas dimensionais não encolhem;
- cotas vêm de H/W/D controlados e nunca da medição do raster;
- saída: STEP6_ENGINEERING_IMAGE_DOCUMENT_FROZEN.

Se o Passo 6 detectar erro físico, deve retornar ao Passo 5.

## 1. Objetivo

Produzir imagens técnicas de painéis PN com aparência consistente, rastreabilidade de engenharia e fidelidade ao projeto, usando o **MODEL 001** como base de composição visual e documental.

A imagem deve comunicar com clareza:
- como o painel é fisicamente organizado;
- quais são suas dimensões reais;
- como a alimentação elétrica é distribuída;
- como os comandos e intertravamentos funcionam;
- como os equipamentos se comunicam;
- quais são os principais equipamentos;
- quais são as premissas de dimensionamento;
- quais são os estados HOLD, quando existirem.

**Frase de controle obrigatória:**

> MODEL 001 DEFINE A FORMA DO DOCUMENTO; O PROJETO DEFINE O TAMANHO, O CONTEÚDO E A ENGENHARIA DO PAINEL.

---

## 2. Regra fundamental: imagem é derivada, nunca fonte de engenharia

A imagem é um artefato downstream.

A sequência obrigatória é:

PREMISSAS CANÔNICAS  
→ DATACENTER  
→ DATASHEET  
→ LI/BOM  
→ SELEÇÃO DOS MODELOS  
→ CARGA ELÉTRICA  
→ UPS/BATERIA  
→ I/O E COMUNICAÇÃO  
→ TÉRMICA  
→ DIMENSIONAMENTO DO GABINETE  
→ LAYOUT DIMENSIONAL  
→ GEOMETRIA  
→ MODEL 001  
→ IMAGEM  
→ QA  
→ MEMÓRIA

É proibido:
- descobrir quantidade olhando a imagem;
- definir potência pela aparência de um equipamento;
- copiar dimensões de outro painel;
- inferir modelo pelo formato visual;
- reduzir componente para caber;
- usar uma imagem gerativa como autoridade dimensional;
- tratar imagem bonita como engenharia aprovada.

---

## 3. Hierarquia das fontes

Antes de elaborar qualquer parte da imagem, respeitar esta ordem:

1. documentos controlados do projeto;
2. premissas canônicas registradas;
3. Data Sheet do painel-alvo;
4. LI/BOM vigente;
5. cálculos elétricos, térmicos, autonomia e I/O;
6. documentação oficial do fabricante;
7. normas aplicáveis;
8. Data Center técnico consolidado;
9. MODEL 001 como composição visual;
10. imagem gerativa somente como representação.

Conflito entre fontes superiores e inferiores:
- prevalece a fonte superior;
- registrar divergência;
- não corrigir silenciosamente;
- usar HOLD quando necessário.

---

## 4. MODEL 001: o que é fixo e o que é variável

### 4.1 O que o MODEL 001 fixa

O MODEL 001 fixa:
- linguagem gráfica;
- composição geral;
- hierarquia visual;
- blocos documentais;
- estilo de títulos;
- uso de fundo branco;
- seções técnicas em azul;
- convenção de tags;
- convenção de cotas;
- relação entre vistas e diagramas;
- estrutura de legenda;
- estrutura de dimensionamento;
- princípio de alta densidade de informação;
- regra de não usar grandes logos de fabricantes como decoração.

### 4.2 O que o MODEL 001 NÃO fixa

O MODEL 001 não fixa:
- altura do gabinete;
- largura do gabinete;
- profundidade do gabinete;
- placa de montagem;
- quantidade de trilhos;
- quantidade/tamanho de canaletas;
- posição dos componentes;
- quantidade de módulos;
- tamanho de bornes;
- UPS;
- baterias;
- fonte;
- climatização;
- cabos;
- disjuntores;
- gateway;
- CPU;
- arquitetura específica de comunicação.

Esses itens são definidos pelo painel-alvo.

---

## 5. Dimensionamento do gabinete é obrigatório antes da imagem

Para cada novo PN, o tamanho do gabinete é uma saída do projeto.

Nunca iniciar por:
> "usar o mesmo tamanho do painel anterior".

O agente deve primeiro dimensionar o conteúdo.

### 5.1 Entradas mínimas para dimensionamento

Considerar:
- LI/BOM completa;
- quantidades físicas reais;
- dimensões oficiais de cada componente;
- folgas obrigatórias do fabricante;
- superfície de montagem;
- trilho DIN;
- placa;
- canaletas;
- bornes;
- reserva de cabos;
- entrada/saída de cabos;
- prensa-cabos;
- raio mínimo de curvatura;
- distribuição de 24 Vcc;
- segregação potência/comando/rede/instrumentação;
- PLC e I/O;
- switch;
- gateway;
- IHM na porta;
- botões/sinaleiros;
- interferência porta × placa;
- UPS;
- baterias;
- climatização;
- dissipação térmica;
- manutenção;
- substituição de componentes;
- peso;
- reserva física;
- restrições de instalação.

### 5.2 Política de reserva

Usar a reserva congelada no projeto.

Quando não houver valor específico, utilizar a premissa vigente do sistema:
- 20% de reserva física;
- sem reduzir folgas mínimas;
- sem usar área de manutenção como "reserva".

### 5.3 Regra de seleção do gabinete

Primeiro calcular necessidade física; depois selecionar um gabinete real de fabricante.

Se não couber:
- não reduzir componente;
- não reduzir canaleta;
- não eliminar acesso;
- não reduzir raio de cabo;
- selecionar gabinete maior;
- ou retornar HOLD_LAYOUT_CAPACITY.

Se faltar dado dimensional:
- retornar HOLD_DIMENSIONAL_DATA.

---

## 6. Congelamento dimensional

Antes do render final devem estar congelados no Data Sheet:
- fabricante/família do gabinete;
- modelo/código;
- altura;
- largura;
- profundidade;
- dimensões úteis;
- placa de montagem;
- porta;
- solução de climatização;
- recortes de porta/lateral;
- reserva física remanescente.

Depois de congelado:
- mudança de componente pode invalidar gabinete;
- mudança de quantidade pode invalidar gabinete;
- mudança de climatização pode invalidar gabinete;
- mudança do gabinete invalida layout, render, QA e emissão;
- qualquer mudança exige revisão controlada.

---

## 7. Estrutura obrigatória da imagem

A composição deve seguir o MODEL 001 e conter, quando aplicável:

### 7.1 Vistas gerais
- vista frontal externa;
- vista frontal interna com porta aberta;
- vista lateral 3/4;
- legenda dos principais componentes;
- dados do quadro.

### 7.2 Arquitetura elétrica
Representar:
- alimentação do painel;
- tensão/fases/aterramento;
- proteção geral;
- DPS;
- proteção da UPS;
- UPS;
- baterias;
- barramento 24 Vcc;
- fonte, quando aplicável;
- climatização;
- PLC;
- switch;
- gateway;
- I/O;
- relés/interfaces;
- instrumentos.

O diagrama deve refletir o circuito real do projeto, não um exemplo genérico.

### 7.3 Arquitetura de comunicação
Representar:
- supervisório/BMS/SCADA;
- switch;
- PLC;
- IHM;
- gateway;
- equipamentos de campo;
- redes e protocolos reais;
- direção lógica das comunicações quando necessário.

Nunca escrever PROFINET, Modbus, BACnet, Ethernet ou outro protocolo sem sustentação documental.

### 7.4 Diagrama de comando
Representar as principais funções:
- emergência local, quando existente;
- comandos locais;
- comandos da IHM;
- comandos remotos/BMS;
- permissivos;
- intertravamentos;
- lógica central no PLC;
- comandos de campo;
- reset;
- setpoint/modo;
- status/feedback/alarmes.

Não inventar DI/DO que não existam na matriz de I/O vigente.

### 7.5 Dimensionamento do painel
Mostrar tabela com:
- H × W × D;
- alimentação;
- aterramento;
- alimentador;
- proteção geral;
- carga de projeto;
- tensão de comando;
- UPS;
- baterias;
- autonomia;
- margem;
- dissipação;
- climatização;
- grau de proteção;
- ambiente.

Dados pendentes devem ser identificados como HOLD.

---

## 8. Regras para cotas

### 8.1 Vista frontal
- largura = largura física real do gabinete;
- altura = altura física real do gabinete;
- cotas baseadas no Data Sheet do painel-alvo.

### 8.2 Vista lateral 3/4
A cota lateral representa **somente a profundidade física real** do gabinete.

Obrigatório:
- utilizar a profundidade do painel-alvo;
- colocar a linha de cota no eixo visível de profundidade/lateral;
- não cotar a largura aparente da perspectiva;
- não copiar profundidade do MODEL 001;
- não deformar perspectiva para coincidir com a cota.

Exemplo do PN-AUT-001:
- profundidade atual: 300 mm;
- este valor é somente da instância PN-AUT-001.

### 8.3 Cotas e geometria
- cotas em mm;
- escala coerente;
- nenhuma dimensão pode ser inventada;
- cota textual deve concordar com o Data Sheet;
- se a geometria for ilustrativa, a cota ainda deve representar o valor real validado.

---

## 9. Regras da vista interna

A vista interna deve:
- representar exatamente a quantidade da LI/BOM;
- manter agrupamento funcional;
- preservar área de canaletas;
- deixar área de bornes acessível;
- mostrar aterramento;
- manter separação de potência e sinal;
- respeitar folgas;
- mostrar a mesma montagem usada pelas demais vistas.

A IHM:
- é uma única instância física;
- fica na porta;
- não deve existir uma segunda IHM na placa;
- na porta aberta, sua traseira pode ser visível, mas continua sendo o mesmo item.

---

## 10. Regras de branding e identificação

Permitido:
- fabricante/modelo escrito em legenda técnica;
- modelo ao lado do equipamento;
- identificação de componente;
- catálogo/código em tabela.

Não permitido:
- logos grandes no rodapé;
- logos decorativos;
- branding que ocupe espaço documental;
- identificação visual que confunda fabricante do componente com fabricante do painel.

---

## 11. Regras de realismo e geração de imagem

A imagem pode utilizar acabamento realista, mas:
- geometria deve vir do projeto;
- proporção não pode ser alterada pelo render;
- materiais/iluminação não podem esconder inconsistência;
- componente não pode ser duplicado por estética;
- não inventar borne, disjuntor, ventilador, relé ou botão;
- não substituir um componente por visual parecido.

A geração visual deve preservar:
- posição relativa;
- quantidade;
- escala;
- orientação;
- tags;
- dimensões;
- fluxo dos diagramas.

---

## 12. Layout da página

Quando o conteúdo aumentar:
- aumentar o canvas;
- não reduzir as vistas de engenharia;
- não comprimir tabelas;
- não ocultar seções obrigatórias;
- priorizar legibilidade.

A página é adaptável.
A engenharia não é adaptável para caber na página.

---

## 13. Paridade obrigatória

Antes de considerar a imagem tecnicamente coerente:

LI = BOM = CARGA = DATASHEET = LAYOUT = GEOMETRIA = IMAGEM

Verificar:
- quantidade;
- tags;
- modelos;
- tensões;
- correntes;
- canais;
- protocolos;
- dimensões;
- arquitetura;
- gabinete;
- UPS/bateria;
- climatização;
- grau de proteção.

Divergência:
- HOLD ou REPROVADO conforme a regra afetada.

---

## 14. QA obrigatório antes de liberar a imagem

Checklist mínimo:

### Dados
- painel correto;
- revisão correta;
- LI correta;
- Data Sheet correto.

### Quantidade
- sem item faltante;
- sem item duplicado;
- IHM única.

### Dimensional
- gabinete do painel-alvo;
- altura correta;
- largura correta;
- profundidade correta;
- cota lateral correta;
- componentes sem distorção.

### Engenharia
- arquitetura elétrica coerente;
- comunicação coerente;
- comando coerente;
- carga coerente;
- UPS/bateria coerentes;
- térmica coerente;
- climatização coerente.

### Visual
- MODEL 001 respeitado;
- fundo branco;
- cabeçalhos técnicos;
- legenda legível;
- sem logos grandes;
- canvas suficiente;
- sem compressão.

### Rastreabilidade
- componentes ligados à documentação oficial;
- Data Center sincronizado;
- memória atualizada;
- alterações registradas.

---

## 15. Estados de saída

### VALIDADO PARA REPRESENTAÇÃO
Pode ser usado quando:
- dados necessários estão fechados;
- paridade comprovada;
- geometria coerente;
- QA visual aprovado.

### HOLD_DIMENSIONAL_DATA
Quando:
- falta dimensão oficial;
- falta profundidade;
- falta folga;
- falta desenho do gabinete/componente.

### HOLD_LAYOUT_CAPACITY
Quando:
- conteúdo não cabe;
- reserva insuficiente;
- manutenção prejudicada;
- cabo/curvatura sem espaço.

### HOLD_ENGINEERING_DATA
Quando:
- carga, comunicação, comando, modelo ou seleção não está fechado.

### REPROVADO
Quando:
- dimensão copiada de outro painel;
- componente distorcido;
- quantidade divergente;
- segunda IHM física;
- protocolo inventado;
- cota incompatível;
- imagem usada para sobrescrever engenharia.

---

## 16. Sincronização obrigatória após elaboração

Depois de aprovar ou alterar significativamente uma imagem:
1. registrar a imagem/modelo no Data Center;
2. registrar SHA-256 ou identificador da referência;
3. atualizar Data Sheet quando houver mudança de projeto;
4. atualizar memória MODEL 001;
5. atualizar memória operacional da conversa/projeto;
6. registrar erros confirmados e regra preventiva;
7. registrar invalidadores downstream;
8. manter histórico append-only.

---

## 17. Perguntas ao usuário

Antes de perguntar:
- pesquisar Data Center;
- pesquisar Data Sheet;
- verificar LI/BOM;
- verificar memória;
- verificar fabricante;
- verificar normas;
- verificar literatura técnica aplicável.

Perguntar somente quando houver decisão real do projeto que não possa ser determinada por fontes.

Quando houver pergunta:
- usar o formato Visualize definido pelo projeto;
- apresentar opções claras;
- disponibilizar no final o bloco consolidado para copiar.

---

## 18. Entradas obrigatórias para nova imagem PN

O agente deve carregar:
- PANEL_ID;
- revisão;
- premissas canônicas;
- LI/BOM;
- catálogo/modelos;
- dimensões;
- matriz I/O;
- carga;
- alimentação;
- UPS/bateria;
- comunicação;
- térmica;
- gabinete selecionado;
- MODEL 001;
- esta Diretriz Mestra.

Se algum item necessário não existir:
- não completar por suposição;
- pesquisar quando possível;
- caso contrário usar HOLD.

---

## 19. Saída de pré-render obrigatória

Antes de chamar qualquer renderizador ou gerador de imagem, produzir internamente:

- PANEL_ID
- REVISION
- MODEL_ID = PN-IMAGE-MODEL-001
- ENCLOSURE_MANUFACTURER
- ENCLOSURE_MODEL
- H_MM
- W_MM
- D_MM
- MOUNTING_PLATE
- PHYSICAL_RESERVE_PERCENT
- LI_REVISION
- LOAD_24VDC
- MAIN_SUPPLY
- UPS_MODEL
- BATTERY_MODEL/CAPACITY
- THERMAL_LOSS_W
- COOLING_MODEL
- IP_REQUIREMENT
- PLC_MODEL
- I/O_SUMMARY
- COMMUNICATION_SUMMARY
- COMMAND_SUMMARY
- DIMENSIONAL_GATE
- LAYOUT_GATE
- PARITY_GATE

Sem isso, não tratar a imagem como representação técnica fechada.

---

## 20. Regra final

A imagem deve parecer profissional porque a engenharia está organizada — nunca organizar a engenharia para fazer a imagem parecer profissional.

**MODEL 001 é a linguagem.  
Data Center + Data Sheet + LI/BOM + cálculos são a verdade.  
O painel real define suas dimensões.  
A imagem apenas representa fielmente essa verdade.**
