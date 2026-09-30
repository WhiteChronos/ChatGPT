# PN-AUT-01 — Base Técnica Consolidada V1

**Estado:** ELÉTRICO INTEGRADO / DADOS A COMPLETAR / RELEASE HOLD / “A DO QUADRO” NÃO INVENTADO

## Arquitetura
Existe somente o **PN-AUT-01**. O **PLC-01** é a autoridade central de automação. Entradas, saídas, comandos, intertravamentos e comunicações devem ser mapeados ao PLC principal ou a I/O remoto pertencente ao mesmo sistema.

## Dados técnicos já confirmados
- **Gabinete NSYCRN86300:** 800 x 600 x 300 mm; IP66; IK10.
- **Fonte ABL8RPS24100:** 24 Vdc / 10 A / 240 W; inrush 30 A; eficiência 87%; perda 31 W.
- **ADEL CBI2420A:** entrada 115-230 Vac; saída 24 Vdc / 20 A; boost 25 A por 4 min; carregador 24 Vdc / 20 A; Modbus RTU.
- **HMIST6500:** 24 Vdc; 12,6 W máx.; inrush até 30 A.
- **SCALANCE X208:** 24 Vdc; 185 mA; 3,84 W; referência legada, sucessor a validar.
- **FIACNXYEKIT:** alimentação **12 Vdc**; interface X/Y/E; até 8 sistemas VRF e 64 unidades internas.
- **PT 2,5 / 3209510:** 800 V; 24 A; 2,5 mm² nominal; 0,14-4 mm².
- **PT 2,5-PE / 3209536:** candidato PE, ainda precisa confirmação de seleção.
- **NS 35/7,5 PERF / 0801733:** trilho 35 x 7,5 mm, 2 m, aço galvanizado.
- **A9F84232 / A9F84210:** sucessores candidatos Schneider; não congelar corrente nominal sem Ib/Iz/Ik.

## HOLDs principais
1. CPU S7-1500 exata.
2. IM/DI/DO/AI/RTD exatos.
3. Lista completa de sinais e matriz de I/O.
4. Alimentação 12 Vdc do gateway Trane.
5. Cargas de campo alimentadas pelo painel.
6. Autonomia e bateria da UPS.
7. Tensão/fases/aterramento reais.
8. Ik/Icc no ponto.
9. Alimentador e método de instalação.
10. Temperatura/altitude.
11. DPS conforme rede/SPDA.
12. Fechamento térmico IEC 61439.

## Regra
Nenhum Excel final deve ser gerado antes de o conjunto mínimo acima estar fechado ou explicitamente aprovado como pendência controlada.
