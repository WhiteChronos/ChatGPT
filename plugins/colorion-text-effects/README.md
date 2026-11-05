# Colorion Text Effects System

Modulo reutilizavel para pesquisar, sincronizar e adaptar efeitos de texto do projeto Colorion Text Effects.

## Componentes

- `SKILL.md`: regras para uso por ChatGPT/agents.
- `references/effects-catalog.json`: snapshot local do catalogo.
- `references/upstream.md`: mapa das fontes oficiais e proveniencia.
- `references/architecture.md`: arquitetura e roadmap.
- `scripts/sync_colorion.py`: atualizador do catalogo a partir do GitHub oficial.
- `scripts/search_effects.py`: pesquisa local sem dependencias externas.

## Uso local

```bash
python scripts/search_effects.py blueprint circuit neon
python scripts/sync_colorion.py --output references/effects-catalog.json
```

O sincronizador usa apenas a biblioteca padrao do Python. Para CI/offline, pode receber um arquivo `effects.ts` local com `--effects-file`.

## Fonte principal

- Site: https://text-effects.colorion.co/
- Upstream: https://github.com/ckissi/colorion-text-effects

Nao trate o snapshot como fonte eterna. Quando a resposta depender do catalogo atual, sincronize primeiro.
