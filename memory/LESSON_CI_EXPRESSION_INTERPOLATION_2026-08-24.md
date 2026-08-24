# Lição: CI e Interpolação de Expressões - 2026-08-24

## Contexto

Este documento registra a lição aprendida sobre interpolação de expressões em workflows GitHub Actions.

## Problema Identificado

O workflow usava referência incorreta à variável de ambiente em steps do CI/CD, causando erros de interpolação.

## Solução Implementada

### Sintaxe Correta de Interpolação

```yaml
# ❌ ERRADO - Não interpola variáveis
env:
  MY_VAR: "valor"
  CONCATENADO: "$MY_VAR/path"  # Não funciona

# ✅ CORRETO - Usa contexto do GitHub Actions
env:
  MY_VAR: "${{ env.MY_VAR }}"
  WORKSPACE: "${{ github.workspace }}"
  BRANCH: "${{ github.ref }}"
```

### Variáveis de Contexto Válidas

| Contexto | Função | Exemplo |
|----------|--------|----------|
| `${{ github.workspace }}` | Diretório raiz do repositório | `/home/runner/work/ChatGPT/ChatGPT` |
| `${{ github.ref }}` | Referência do Git (branch/tag) | `refs/heads/main` |
| `${{ github.event }}` | Evento que disparou o workflow | `push`, `pull_request` |
| `${{ env.VAR_NAME }}` | Variável de ambiente | Acesso a vars definidas em `env:` |

### Padrão Adotado no Projeto

```yaml
env:
  PYTHONPATH: ${{ github.workspace }}
  PYTHONDONTWRITEBYTECODE: '1'
  PYTHONUNBUFFERED: '1'
  CI: 'true'

steps:
  - name: Verify CI environment contract
    run: |
      test "$PYTHONPATH" = "$GITHUB_WORKSPACE"  # Compara variáveis shell
      python -c "import pipeline.validate_engineering"
```

## Resultados

- ✅ Workflows agora usam interpolação correta
- ✅ Variáveis de ambiente resolvidas corretamente
- ✅ Compatibilidade com POSIX shell mantida
- ✅ Debugging facilitado

## Recomendações

1. Sempre usar `${{ github.workspace }}` para paths absolutos
2. Documentar variáveis de contexto esperadas em cada step
3. Testar localmente com `act` (GitHub Actions local runner)
4. Usar `env:` para variáveis compartilhadas entre steps
5. Manter consistência de nomeação (UPPERCASE para env vars)

## Referências

- [GitHub Actions - Context Documentation](https://docs.github.com/en/actions/learn-github-actions/contexts)
- [GitHub Actions - Environment Variables](https://docs.github.com/en/actions/learn-github-actions/environment-variables)
