# PROMPT — PN IMAGE MODEL 001 / ELABORAÇÃO DE PAINÉIS PN

ID: PROMPT-PN-IMAGE-MODEL-001
Status: MANDATORY
Purpose: instruir Codex/agentes de engenharia a usar o MODEL 001 como estrutura documental e visual, sem transformar as dimensões do PN-AUT-001 em padrão físico para outros painéis.

## 1. Princípio central
O MODEL 001 é a base de COMPOSIÇÃO do documento, não um gabinete de dimensões fixas.

Para cada novo painel PN:
- reaproveitar a estrutura visual, hierarquia, seções, estilo de cotagem, linguagem gráfica e sequência documental;
- recalcular o tamanho físico do gabinete a partir do projeto específico;
- nunca copiar automaticamente altura, largura, profundidade, placa de montagem, quantidade de trilhos, canaletas ou posições do PN-AUT-001.

## 2. Ordem obrigatória de elaboração
Antes de criar qualquer imagem:
1. Carregar as premissas canônicas do painel-alvo.
2. Carregar Data Center e Data Sheet do painel-alvo.
3. Carregar LI/BOM congelada e revisão vigente.
4. Confirmar fabricante/modelo e dimensões oficiais de cada componente.
5. Confirmar quantidade física exata de cada item.
6. Carregar cargas elétricas, UPS/bateria, comunicação e dados térmicos.
7. Calcular espaço real necessário e selecionar o gabinete.
8. Congelar dimensões do gabinete no Data Sheet do painel-alvo.
9. Elaborar layout dimensional em escala comum.
10. Somente então gerar a imagem baseada no MODEL 001.
11. Executar QA LI = BOM = CARGA = LAYOUT = IMAGEM.

## 3. Dimensionamento obrigatório do gabinete
O tamanho do painel deve ser definido pelo conteúdo real do quadro e pelas restrições do projeto.

Considerar obrigatoriamente:
- dimensões oficiais de todos os componentes;
- folgas de montagem do fabricante;
- raio de curvatura de cabos;
- canaletas, trilhos DIN, bornes e zona de entrada/saída de cabos;
- separação entre potência, comando, comunicação e instrumentação;
- IHM e dispositivos na porta;
- interferência porta x placa de montagem;
- UPS e baterias;
- gateway, switch, PLC, I/O e expansões;
- dissipação térmica e geometria do sistema de climatização;
- acesso para manutenção e substituição;
- reserva física mínima congelada no projeto, por padrão 20% quando aplicável;
- peso, montagem, acesso de prensa-cabos e aterramento;
- requisitos IP/IK e método de instalação.

Regra:
NÃO escolher o gabinete primeiro e forçar os componentes a caber.
Primeiro dimensionar o conteúdo; depois selecionar um gabinete real de fabricante que atenda.

## 4. Regra de dimensões
As dimensões do MODEL 001 usadas no PN-AUT-001 são apenas EXEMPLO DE INSTÂNCIA.

- PN-AUT-001: referência atual 1800 x 800 x 300 mm, se confirmado pelo Data Sheet vigente.
- Outro PN: deve possuir dimensões próprias determinadas por sua engenharia.
- A profundidade mostrada na vista lateral 3/4 deve ser a profundidade REAL do painel-alvo.
- A linha de cota deve acompanhar o eixo real de profundidade/lateral, nunca a largura projetada da perspectiva.
- Se a dimensão ainda não estiver fechada: usar HOLD_DIMENSIONAL_DATA; não inventar.

## 5. Estrutura visual obrigatória do MODEL 001
A imagem final deve conter, quando aplicável:
1. Vista frontal externa.
2. Vista frontal interna com porta aberta.
3. Vista lateral 3/4 com cota de profundidade real.
4. Legenda dos principais componentes.
5. Dados do quadro.
6. Arquitetura elétrica / potência e controle.
7. Arquitetura de comunicação.
8. Diagrama de comando / principais funções.
9. Dimensionamento do painel.
10. Identificação do painel e revisão.

## 6. Regras de composição
- Fundo branco.
- Títulos de seção em azul técnico.
- Tags consistentes.
- Setas e fluxos legíveis.
- Cotas em mm.
- Não distorcer componente para caber.
- Não duplicar componentes físicos.
- IHM de porta aparece uma única vez como componente físico.
- Não usar logos grandes de fabricantes como decoração ou rodapé.
- Fabricante/modelo pode aparecer somente como informação técnica.
- Não usar imagem gerativa como autoridade dimensional.
- Se a geometria real divergir do MODEL 001, preservar a engenharia e adaptar o layout da página, nunca a geometria do painel.

## 7. Autoridade dos dados
Ordem de autoridade:
1. Documento controlado do projeto / premissas canônicas.
2. Data Sheet do painel-alvo.
3. LI/BOM vigente.
4. Cálculos elétricos, térmicos e de autonomia.
5. Documentação oficial de fabricante.
6. MODEL 001 como estrutura visual.
7. Imagem gerativa apenas como representação.

O MODEL 001 nunca pode sobrescrever os itens 1 a 5.

## 8. Critério de gabinete
O agente deve produzir uma decisão rastreável:
- componentes considerados;
- áreas ocupadas;
- folgas;
- reserva;
- área/volume necessários;
- solução térmica;
- gabinete candidato;
- dimensões finais;
- margem remanescente.

Se o gabinete candidato não comportar o projeto em escala real:
- NÃO reduzir componentes;
- NÃO reduzir espaçamentos obrigatórios;
- selecionar gabinete maior ou emitir HOLD_LAYOUT_CAPACITY.

## 9. Mudanças
Após congelar o gabinete no Data Sheet do painel-alvo:
- mudança de componente/dimensão/quantidade pode invalidar o gabinete;
- mudança de gabinete invalida layout, render, QA e documentos dependentes;
- registrar nova revisão e impacto.

## 10. Saída esperada
Antes de renderizar, emitir internamente:
- PANEL_ID
- REVISION
- LI/BOM source
- enclosure manufacturer/model
- H x W x D
- mounting plate size
- physical reserve %
- load current / UPS
- thermal loss / cooling model
- communication architecture
- layout status
- dimensional gate status

Renderizar somente se os dados necessários estiverem fechados; caso contrário retornar HOLD.

## 11. Frase de controle
"MODEL 001 DEFINE A FORMA DO DOCUMENTO; O PROJETO DEFINE O TAMANHO E O CONTEÚDO DO PAINEL."
