# Evals — Comment Control

Executa casos contra o caminho real do agente e aplica graders determinísticos.

## Executar

```bash
python -m evals.run_local
```

Requer `OPENAI_API_KEY` no ambiente. O arquivo `evals/results/latest.json` registra o resultado local.

## O que é testado

- preservação da quantidade formal;
- preservação dos IDs e ordem;
- proibição de `CHECKED` automático;
- separação de novas divergências;
- rastreabilidade de comentários multi-documento.

Os graders não avaliam estilo de prosa. Avaliam comportamento contratual e integridade.
