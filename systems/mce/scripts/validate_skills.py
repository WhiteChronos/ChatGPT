from pathlib import Path
import yaml

root=Path(__file__).resolve().parents[1]/'.agents/skills'
expected=('padronizacao-mce','engenharia-mce-projeto','mce-fechamento-operacional')
for name in expected:
    p=root/name/'SKILL.md'
    data=p.read_text(encoding='utf-8')
    assert data.startswith('---\n'),p
    fm=yaml.safe_load(data.split('---',2)[1])
    assert fm['name']==name and fm['description'] and set(fm)=={'name','description'}
    assert (root/name/'agents/openai.yaml').exists()
print('OK: 3 skills com frontmatter, nome e metadados validos.')
