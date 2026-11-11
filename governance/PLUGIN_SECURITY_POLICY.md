# Política de Plugins e Ferramentas Externas — v1.0

## Objetivo

Manter um catálogo permanente de ferramentas de apoio à elaboração e validação documental sem permitir instalação automática insegura ou alteração silenciosa das regras de engenharia.

## Regras

1. Descoberta não significa aprovação.
2. Nenhuma ferramenta é instalada automaticamente a partir de busca do GitHub.
3. Toda candidata deve ter repositório canônico identificado.
4. Devem ser avaliados licença, atividade recente, histórico de segurança, dependências, manutenção, reprodutibilidade e compatibilidade.
5. Versões aprovadas devem ser fixadas por versão e hash.
6. A ferramenta deve operar sob o princípio de menor privilégio.
7. A ferramenta nunca pode alterar o padrão documental sem autorização.
8. Saídas devem passar por testes de regressão e inspeção visual.
9. Ferramentas para arquivos Office com macros devem ser tratadas como alto risco.
10. O catálogo deve ser revisado periodicamente pelo workflow de descoberta.

## Estados do catálogo

- `DISCOVERED`: localizada, ainda não avaliada;
- `EVALUATION`: em avaliação técnica e de segurança;
- `APPROVED_OPTIONAL`: aprovada para uso controlado;
- `APPROVED_CORE`: aprovada para o pipeline principal;
- `BLOCKED`: reprovada;
- `RETIRED`: removida de uso.

## Proibição de auto-instalação

O registro `auto_install` deve permanecer `false` para todas as ferramentas. A promoção para dependência do pipeline exige PR próprio, testes, revisão e aprovação.
