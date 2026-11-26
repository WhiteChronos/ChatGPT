# Regras de engenharia e verificacao logica
1. Fonte primaria = documentos aprovados da engenharia; cada causa e efeito possuir vinculo verificavel a tag, desenho e revisao.
2. Grafo de P&ID G=(V,E) representa ativos e conectividade fisica/sinais documentados; grafo de intertravamento H=(C,F,R) representa causas C, efeitos F e relacoes R documentadas. **Nao inferir H automaticamente de G.**
3. Votacao m-de-n: efeito habilitado quando soma dos detectores validos ativos >= m, conforme filosofia/SRS; tratar falha de detector separadamente. Nunca inventar m ou n.
4. Verificacao: tabela verdade para AND/OR/votacao; estados normal, falha, manutencao, bypass, startup, shutdown; testes de reset e persistencia; temporizadores e sequencia.
5. Indicar `N/A` apenas se fonte justificar inaplicabilidade; usar `PENDENTE` se desconhecido; nao confundir ausencia de evidencias com ausencia de efeito.
6. Referencias de pesquisa: https://github.com/Azure-Samples/digitization-of-piping-and-instrument-diagrams ; https://github.com/S-Houston/digitised-pid-mlops ; https://www.pi-research.org/project/flowsheet-digitization/ ; https://www.isa.org/standards-and-publications/isa-standards/isa-18-series-of-standards ; https://webstore.iec.ch/
