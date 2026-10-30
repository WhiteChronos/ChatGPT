# Arquitetura MCE independente

1. Inventário e contrato do XLSX mestre com revisão humana.
2. Leitura de fontes P&ID e listas I/O via adaptadores locais; apenas evidência candidata.
3. Relatório de entendimento e STOP obrigatório.
4. Autorização de células e de elaboração vinculada a evidências SHA.
5. Edição OOXML controlada de cópia do arquivo Excel, seguida por auditoria e revisão técnica.

Este sistema é autônomo e não contém servidor MCP, ferramentas de engenharia reversa ou dependência de outros produtos.

6. Orquestrador `matriz-causa-efeito`: importa tres formatos GitHub pelas APIs locais `mce_system.py`/`pid_bridge.py`, gera DataSheet privado, escreve evento no SQLite MCE, mantem aprovacao humana como gate e preserva um unico editor OOXML.
