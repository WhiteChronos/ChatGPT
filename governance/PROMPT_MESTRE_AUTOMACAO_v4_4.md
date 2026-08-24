# Prompt Mestre - Automação v4.4

## Especificações Técnicas

### Medições de Resolução
- Resolução padrão: **12 mm**
- Aspecto de proporção: 1:1

### Estados de Processamento
Os estados válidos do processamento são:
- **CMD**: Comando recebido e aceito
- **RUN**: Comando em execução
- **FAULT**: Erro ou falha detectada

## Fluxo de Automação v4.4

1. Recepção do comando (CMD)
2. Validação de entrada
3. Execução da tarefa (RUN)
4. Tratamento de erros (FAULT)
5. Retorno do resultado

## Constantes de Configuração

```json
{
  "resolution_mm": 12,
  "aspect_ratio": 1,
  "states": ["CMD", "RUN", "FAULT"]
}
```
