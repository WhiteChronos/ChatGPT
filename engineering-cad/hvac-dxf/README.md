# HVAC Manufacturer DXF Toolkit

Pipeline versionado para transformar listas de equipamentos e fichas tecnicas em blocos DXF rastreaveis.

## Regra de ouro
Nao inventar geometria. A cadeia obrigatoria e:
**fabricante -> modelo exato -> catalogo oficial -> ficha/desenho dimensional -> CAD/BIM nativo -> DXF validado**.

## Padrao CAD
- Model Space 1:1
- unidade: metro
- fonte: Arial
- preservar geometria nativa do fabricante
- manter vistas FRONT/LEFT/RIGHT/TOP quando existirem
- registrar furação, bases, conexoes, grelhas, ventiladores, paineis e pontos de manutencao presentes no desenho de origem

## Estrutura
- `sources/`: proveniencia e fontes do fabricante
- `manifests/`: modelos, desenhos, revisoes e status
- `blocks/`: DXFs aprovados
- `scripts/`: validacao e normalizacao
- `memory/`: memoria tecnica versionada
- `skills/hvac-manufacturer-dxf/`: skill reutilizavel
- `open-source/`: registro de ferramentas OSS

## Classes de confiabilidade
- `CAD_FABRICANTE`: CAD/BIM nativo do fabricante ou copia de catalogo tecnico autorizado
- `RECONSTRUCAO_FICHA`: redesenho a partir de desenho dimensional oficial
- `REFERENCIA_PROJETO`: familia/envelope de projeto; nao usar para interferencia ou fabricacao
