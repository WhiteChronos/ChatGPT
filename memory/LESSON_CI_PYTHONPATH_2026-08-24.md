# Lição aprendida — importação Python no GitHub Actions

## Identificação
- Categoria: REGRESSION / LESSON
- Data: 2026-08-24
- Componente: `.github/workflows/engineering-governance.yml`
- Sintoma: `pytest` não conseguia importar módulos do pacote `pipeline` no ambiente do GitHub Actions.

## Causa
O diretório raiz do workspace não estava garantido explicitamente no `PYTHONPATH` durante a execução de testes. A chamada direta `pytest -q` também dependia do comportamento do executável instalado no ambiente.

## Correção
1. Definir `PYTHONPATH: ${{ github.workspace }}` no nível do job.
2. Executar testes com `python -m pytest -q`.
3. Adicionar uma etapa de contrato do ambiente que importa explicitamente `pipeline.validate_engineering` e `pipeline.agents_v4_4`.
4. Adicionar uma verificação do próprio workflow para impedir remoção acidental do `PYTHONPATH` e do comando `python -m pytest`.
5. Fixar a dependência de teste em `requirements-dev.txt` para melhorar reprodutibilidade.

## Regra preventiva
Nenhuma alteração do workflow de governança pode remover o `PYTHONPATH` do workspace, alterar o runner de testes para uma forma que dependa de PATH implícito ou remover o teste de importação sem uma substituição tecnicamente equivalente e revisada.

## Critério de regressão
O CI deve falhar se:
- `$PYTHONPATH != $GITHUB_WORKSPACE`;
- `import pipeline.validate_engineering` falhar;
- `import pipeline.agents_v4_4` falhar;
- o workflow deixar de conter o contrato explícito de `PYTHONPATH`;
- a suíte de regressão falhar.

## Observação
Esta memória registra uma falha de infraestrutura. Ela não altera regras de engenharia AUTOMAÇÃO DM, mas integra o mesmo princípio de governança: erro detectado → lição → regra preventiva → teste de regressão.