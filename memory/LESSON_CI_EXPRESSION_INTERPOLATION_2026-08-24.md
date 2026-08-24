# Lição aprendida — interpolação de expressão no GitHub Actions

Data: 2026-08-24
Categoria: REGRESSION / CI

## Ocorrência
Um passo do workflow tentou conferir o texto literal da configuração de PYTHONPATH usando grep sobre o próprio arquivo YAML. O mecanismo do GitHub Actions substituiu a expressão de workspace pelo caminho real antes da execução do shell. Por isso, o grep procurou o caminho expandido dentro do YAML, embora o arquivo armazenasse apenas a expressão de workspace. O comando terminou com código 1 mesmo com o PYTHONPATH correto em tempo de execução.

## Causa raiz
Mistura de dois níveis de interpretação: expressão do GitHub Actions e shell. A expressão foi avaliada antes de o comando chegar ao shell.

## Correção
1. Remover a verificação textual autorreferente por grep.
2. Validar em runtime comparando PYTHONPATH com GITHUB_WORKSPACE.
3. Validar o contrato textual em teste Python, lendo o YAML como texto.

## Regra preventiva
Não verificar dentro de um comando run do próprio workflow uma expressão do GitHub que precise permanecer literal no arquivo. Preferir teste Python ou parser YAML.

## Regressão automatizada
O arquivo tests/test_ci_workflow_contract.py deve exigir a declaração de PYTHONPATH baseada no workspace, exigir python -m pytest e proibir o grep autorreferente que causou a falha.

## Melhoria adicional
As ações oficiais foram atualizadas para checkout v7 e setup-python v7, compatíveis com Node 24. O checkout também desativa persistência de credenciais porque este job não executa push.
