# PN-AUT-001 — External Technical Knowledge Base

Generated: 2026-09-29

## Storage policy
This file is the human-readable companion to the structured external-source registry. Full copyrighted standards, books and papers are not copied. The Data Center stores source metadata, official links, concise engineering summaries, project application and validation status.

## Strong findings now stored

### Short-circuit
IEC 60909 is the calculation basis. The prospective fault current at PN-AUT-001 is derived from the upstream network/source and intervening impedances. A breaker manufacturer's Icu/Icn is a device capability and is not a substitute for site Ik/Icc.

Schneider's Electrical Installation Guide is retained as a manufacturer technical guide for the impedance method, cable sizing, voltage drop and protection coordination.

### Cable sizing
The 2.5 mm2 Cu, 2F+PE, 10 m multipolar exposed feeder remains a preliminary candidate only. Final closure requires final Ib, 40 C derating, installation/arrangement confirmation, voltage-drop check, short-circuit thermal withstand and protective-device coordination.

### HMI
HMIST6500 remains frozen. Official Schneider data: 24 Vdc nominal, 19.2-28.8 Vdc input range, 12.6 W maximum power, inrush up to 30 A.

### Analog I/O
6ES7134-6TD00-0CA1 remains the strong candidate for the 67 installed 2-wire 4-20 mA + HART inputs. Seventeen 4-channel modules provide 68 channels. BaseUnits and segment-power architecture are still to be frozen.

### Temperature
NOVUS TEMP-WM is retained only as the original wall-mount reference and is not acceptable as the final transmitter while HART is mandatory.
NOVUS TxIsoBlock HRT / TxIsoRail HRT and Siemens SITRANS TF320 are HART-capable alternatives, but require an engineered ambient-wall sensing arrangement rather than being direct compact TEMP-WM equivalents.

### CO2
ATI D12Ex-IR and Omniguard Model 3100 are research candidates for 0-5000 ppm + 4-20 mA + HART. Both require application review because they are industrial gas-detection products, not ordinary HVAC IAQ wall sensors.

### Trane VRF gateway
The official Trane TVR Smart controls page lists TCONTSMCB24V under Gateways and exposes the official PDF:
https://www.trane.com.br/content/dam/Trane/Commercial/lar/br/produtos-sistemas/equipamentos/Sistema_VRF/TVR%20Smart/Controles/Gateways/iom-pb-tvr-tvr-smart-acessories-50-60hz-tcontsmcb24v-vrf-svn127a-pb.pdf

This is a stronger lead than third-party gateways. However, model naming is not accepted as proof of 24 Vdc input. The PDF technical content must still be extracted and checked for supply, protocol and exact TVR-family compatibility.

### UPS
CBI2420A remains a documented DC-UPS/charger candidate. Project autonomy is 30 minutes and all 24 Vdc panel equipment is inside the backed-up load scope. Battery capacity cannot be frozen until the final 24 Vdc load is closed.

### Thermal management and IP66
IEC 60529 is retained for enclosure IP verification and IEC 61439-1 for assembly verification/temperature-rise. Schneider ClimaSys CU is a candidate closed-loop cooling family. Final release requires thermal sizing and evidence that the modified assembled enclosure retains IP66.

## Academic / independent technical layer
- Phase to Phase, Networks for Electricity Distribution, Chapter 8 — independent technical explanation of IEC 60909 short-circuit methods.
- MDPI Energies (2026), DOI 10.3390/en19112510 — peer-reviewed review of short-circuit calculation/protection methods including IEC 60909 and model limitations.
- Secondary cable-sizing handbooks are stored only as explanatory support. IEC 60364/IEC 60287 and project/national requirements remain authoritative.

## Release discipline
External research can reduce HOLDs, but cannot invent missing site data. If the source does not prove the exact model, voltage, protocol, lifecycle, IP or application suitability, the item stays HOLD.
