# Cenarios de validação

- Aceitar estrutura de adjacencia Azure e manter efeitos vazios; rejeitar resposta job_status, IDs duplicados e direção inválida.
- Avisar assets faltantes, TAGs OCR repetidos e texto com formula em CSV.
- Calcular efeitos de exemplo não cobertos sem erro de sombreamento de variável.
- Rejeitar causas/efeitos referenciados fora do catálogo.
- Comparar I/O sem concluir segurança; validar SHA de origem, rejeitar origem externa e dados adulterados.
- Exigir revisao humana de cada derivado para produzir relatório de entendimento.
- Rejeitar edicao de Excel sem aprovacao, formula, cabeçalho, celula colorida e exceder 50 causas.
- Verificar diferença OOXML e original preservado após edição de fixture.

Evidencia automatizada: `python -m pytest -q tests`; evidência humana de projeto real: ainda pendente.
