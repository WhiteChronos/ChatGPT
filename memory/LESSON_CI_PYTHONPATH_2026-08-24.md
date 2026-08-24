# Lição: CI e PYTHONPATH - 2026-08-24

## Contexto

Este documento registra a lição aprendida sobre configuração de PYTHONPATH em workflows de CI/CD.

## Problema Inicial

O workflow não conseguia importar módulos do projeto porque o PYTHONPATH não estava configurado corretamente.

## Solução Implementada

### Configuração Correta

```yaml
env:
  PYTHONPATH: ${{ github.workspace }}
  PYTHONDONTWRITEBYTECODE: '1'
  PYTHONUNBUFFERED: '1'
```

### Verificação no Workflow

```bash
test "$PYTHONPATH" = "$GITHUB_WORKSPACE"
python -c "import pipeline.validate_engineering; import pipeline.agents_v4_4"
```

## Resultados

- ✅ Imports funcionando corretamente
- ✅ Módulos do `pipeline/` são importáveis
- ✅ CI/CD passa sem erros de path

## Recomendações

1. Sempre definir PYTHONPATH em variáveis de ambiente do workflow
2. Testar imports explicitamente em passos de CI
3. Documentar estrutura de diretórios para novos contribuidores
4. Manter sincronizado com documentação de setup local
