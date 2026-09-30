# PROMPT MASTER — ELABORAÇÃO COMPLETA DE PROJETO PN — V1

**ID:** PROMPT-MASTER-ELABORACAO-PROJETO-PN-V1
**Status:** MANDATORY / CONTROLLED
**Aplicação:** todo novo painel PN e toda revisão de painel PN existente
**Modelo visual:** PN-IMAGE-MODEL-001
**Diretriz visual:** PROMPT-DIRETRIZ-IMAGEM-PN-V1

## REGRA CENTRAL

> O projeto governa os dados. A LI/BOM governa as quantidades. O Data Sheet governa a revisão do painel. O MODEL 001 governa somente a forma do documento visual.

Nunca usar imagem, memória informal ou painel anterior para sobrescrever dados canônicos.

## ETAPA 0 — BOOTSTRAP E CONFLITOS

1. Identificar PANEL_ID e revisão.
2. Carregar premissas canônicas, Data Center, Data Sheet, LI/BOM, memória, Golden Rules, pipeline, MODEL 001 e diretriz de imagem.
3. Reconciliar dimensões, quantidades, topologia, modelos, cargas, protocolos e HOLDs.
4. Se houver conflito entre Excel, imagem e Data Sheet, bloquear o downstream até determinar a fonte de autoridade.
5. Registrar o conflito, a decisão e quais artefatos ficaram inválidos.

## ETAPA 1 — LEVANTAMENTO DO PROJETO

Levantar:
- lista de equipamentos de campo;
- equipamentos internos do quadro;
- quantidade de unidades HVAC internas e externas;
- sinais hardwired;
- sinais analógicos;
- HART;
- redes;
- gateways;
- comandos;
- feedbacks;
- alimentação;
- autonomia;
- ambiente;
- grau de proteção;
- requisitos de manutenção e expansão.

Nenhum equipamento pode ficar sem destino lógico/físico.

## ETAPA 2 — PESQUISA TÉCNICA

Para cada item:
1. localizar fabricante oficial;
2. localizar modelo/família;
3. localizar manual/datasheet/CAD;
4. verificar lifecycle;
5. verificar alimentação;
6. verificar consumo;
7. verificar dimensões;
8. verificar montagem;
9. verificar interfaces;
10. verificar capacidade máxima;
11. registrar documento, revisão, página/seção, link, data e aplicação no projeto.

Usar primeiro fabricante oficial. Plugins de pesquisa servem para descoberta e coleta, não como autoridade final.

## ETAPA 3 — ARQUITETURA DE AUTOMAÇÃO

Criar inventário de endpoints.

Para cada gateway/interface distinguir:
- quantidade de conectores físicos;
- quantidade de buses;
- quantidade de dispositivos por bus;
- quantidade de endereços;
- quantidade máxima de unidades internas;
- quantidade máxima de unidades externas/sistemas;
- protocolos;
- alimentação;
- topologia permitida.

Nunca chamar limite de endereços de "portas" sem confirmar a natureza do limite.

Criar tabela:
ORIGEM -> INTERFACE -> REDE/BUS -> GATEWAY -> EQUIPAMENTOS -> QUANTIDADE -> CAPACIDADE -> UTILIZAÇÃO -> RESERVA.

Se quantidade requerida > capacidade: REPROVADO/HOLD até redimensionar a arquitetura.

## ETAPA 4 — I/O E COMUNICAÇÃO

1. Elaborar matriz I/O.
2. Elaborar matriz de comunicação.
3. Mapear todos os pontos ao PLC/gateway.
4. Verificar canais e 20% de reserva quando essa premissa estiver vigente.
5. Verificar módulos, BaseUnits, interfaces e acessórios.
6. Fechar protocolos e endereçamento.
7. Reconciliar I/O com LI/BOM.

## ETAPA 5 — SELEÇÃO DE COMPONENTES

Selecionar:
- PLC/CPU;
- I/O;
- switch;
- gateways;
- fontes;
- UPS;
- baterias;
- proteções;
- DPS;
- relés/interfaces;
- bornes;
- cabos;
- gabinete;
- climatização;
- instrumentos.

Exigir compatibilidade integral e documentação oficial.

## ETAPA 6 — CARGA E DIMENSIONAMENTO ELÉTRICO

Calcular:
- carga 24 Vcc;
- carga CA;
- reserva;
- fonte;
- UPS;
- autonomia;
- bateria;
- Ib;
- In;
- Iz;
- queda de tensão;
- Icu versus Ik quando Ik estiver disponível;
- DPS;
- perdas térmicas;
- corrente nominal do conjunto;
- verificações aplicáveis de Icw/Ipk.

"A DO QUADRO" somente após fechamento do gate elétrico.

## ETAPA 7 — LI/BOM

1. LI antes do desenho.
2. Quantidades rastreáveis.
3. Modelos exatos.
4. Acessórios obrigatórios incluídos.
5. Gateway dimensionado para a quantidade real de equipamentos.
6. Mudança de quantidade/modelo cria nova revisão e invalida downstream.

## ETAPA 8 — DIMENSIONAMENTO FÍSICO DO QUADRO

O tamanho do quadro é variável por projeto.

Dimensionar a partir de:
- componentes;
- folgas;
- canaletas;
- trilhos;
- bornes;
- cabos;
- raio de curvatura;
- entrada/saída;
- porta;
- IHM;
- UPS/baterias;
- climatização;
- manutenção;
- reserva física.

Selecionar gabinete real somente depois de provar capacidade.

Nunca copiar H x W x D do MODEL 001 ou de outro PN.

## ETAPA 9 — LAYOUT

1. Uma escala em mm.
2. Uma única instância física de cada item.
3. IHM somente na porta.
4. Separação funcional.
5. Acesso de manutenção.
6. Canaletas e bornes dimensionados.
7. Validar profundidade.
8. Validar interferência porta x placa.
9. Validar climatização e recortes.
10. Validar reserva remanescente.

## ETAPA 10 — IMAGEM / MODEL 001

Carregar obrigatoriamente:
- PN_MODEL_001;
- PROMPT_DIRETRIZ_ELABORACAO_IMAGEM_PN_V1.

Gerar:
- vista frontal externa;
- vista frontal interna;
- vista lateral 3/4;
- legenda/dados;
- arquitetura elétrica;
- arquitetura de comunicação;
- diagrama de comando;
- dimensionamento do painel.

A cota lateral deve representar somente a profundidade real do painel-alvo.

## ETAPA 11 — QA CRUZADO

Verificar:
LI = BOM = CARGA = I/O = COMUNICAÇÃO = DATASHEET = LAYOUT = GEOMETRIA = IMAGEM.

Rejeitar:
- dimensões desatualizadas;
- gateway subdimensionado;
- quantidade divergente;
- protocolo inventado;
- componente duplicado;
- item sem fonte;
- imagem com dado antigo.

## ETAPA 12 — MEMÓRIA E DATACENTER

Após todo marco:
- registrar decisão;
- registrar erro;
- registrar solução;
- registrar fonte;
- registrar mudança de premissa;
- registrar invalidadores;
- atualizar memória do painel;
- atualizar memória metodológica;
- atualizar Data Center.

## ETAPA 13 — EVOLUÇÃO CONTROLADA

O sistema pode:
- detectar padrões de erro;
- sugerir novos checks;
- sugerir automações;
- propor ferramentas;
- propor novas regras;
- propor testes de regressão.

O sistema não pode:
- alterar Golden Rules automaticamente;
- aprovar engenharia automaticamente;
- apagar HOLD;
- promover fato sem evidência;
- alterar revisão congelada sem controle.

Toda evolução = PROPOSTA -> SIMULAÇÃO -> QA -> HUMAN GATE -> VERSÃO.

## PLUGINS / FERRAMENTAS

Usar quando disponíveis:
- Tavily / Firecrawl: pesquisa e crawl de fabricantes/documentação;
- Scite: literatura científica e verificação acadêmica;
- Wolfram: cálculo rigoroso;
- Airtable: índice estruturado de componentes, fontes, HOLDs, modelos e revisões;
- Coda / Notion: base de conhecimento e documentação operacional;
- Acumen: sinalização de lacunas de contexto recente; toda informação deve ser reverificada;
- GitHub/Codex: fonte auditável, versionamento, QA e automação.

Plugins nunca substituem documentação oficial.

## FRASE DE CONTROLE

**NÃO PERDER A REFERÊNCIA DO MODELO:**
MODEL 001 = estrutura visual.
Data Sheet = painel/revisão.
LI/BOM = quantidades/modelos.
Data Center = evidências.
Memória = decisões/erros/aprendizado.
Pipeline = ordem obrigatória.
