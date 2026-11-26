# Integrações P&ID por formatos documentados no GitHub

Inspecionados em 2026-10-28 (árvore, README e contratos inspecionados em código aberto):

1. `Azure-Samples/digitization-of-piping-and-instrument-diagrams` no commit `c51302e3ec34147c676ef6eedbdd7551ea908b05`, MIT: contrato `assets[].connections[]`, direção não confiável para lógica. Adaptador JSON próprio.
2. `S-Houston/digitised-pid-mlops` no commit `f0165e6477be7d891ee2d2403a65e474f484cb17`, licença não identificada: CSV `filename,consolidated_text`; adaptador OCR próprio.
3. `ZzzJjt/Industrial-Control` no commit `df9751647f92ea91ff8f51e985f8dbb6e663f380`, licença não identificada: exemplo não normativo; upstream possui sombreado de `effect_list` no validador de cobertura. Adaptador de intercâmbio JSON local e validação independente.

Ações permitidas: catalogar, normalizar exportações em arquivo separado, verificar consistência e registrar SHA. Ações bloqueadas: copiar código não licenciado, usar OCR como TAG verificada, criar efeito MCE sem narrativa/SRS, alterar Excel, enviar fontes para Azure/AWS, aprovar sem usuário.

Scripts: `scripts/pid_bridge.py`; no pacote integrado, use `scripts/mce_system.py` na raiz. O workflow gera derivados pendentes e exige o campo `pid_integration_review[]` no JSON do relatório de entendimento. O processamento é local e independente de outros sistemas.
