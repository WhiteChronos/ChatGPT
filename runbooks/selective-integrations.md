# Governanca de integracoes seletivas — WhiteChronos

**Autoridade:** GitHub `WhiteChronos/ChatGPT`. **Painel operacional:** [Issue #95](https://github.com/WhiteChronos/ChatGPT/issues/95). **Plano:** [2026-10-14-selective-integration-registry.md](../docs/superpowers/plans/2026-10-14-selective-integration-registry.md).

## Objetivo e modelo de confianca

Integrar *somente os pontos de entrada e contratos aprovados* de provedores externos, sem copiar indiscriminadamente suas aplicacoes, hooks, agentes, servidores MCP ou credenciais. Esta camada e um registro e uma prova de politica estaticos; **nao instala nem executa provedores**.

O inventario vive em `registry/integrations/index.json` e seus descritores seguem `schema.json`. A selecao explicita vive em `registry/integrations/selection-policy.json`. Os hashes e licencas sao confrontados com os locks dos quatro controllers.

| Capacidade | Fonte / modo | Limite de ativacao |
|---|---|---|
| Superpowers oficial | `superpowers@openai-curated`, fluxo oficial | Processo preferencial de planejamento/TDD/revisao; uma copia `vendor/obra-superpowers` nao prova plugin carregado |
| ECC | `affaan-m/ECC`, especialistas | Invocar quando a area tecnica justificar; hooks e MCPs nao sao registrados por este descritor |
| Matt Pocock | skills estaveis gerenciadas em projeto | Respeitar `user-invoked` versus `model-invoked`; nao instalar uma segunda copia global |
| Awesome LLM Apps | catalogo de exemplos, somente referencia | Sem executar exemplos, containers, agentes autonomos ou integracoes credentialed |
| GitHub Arena e Broker | adaptadores internos registrados previamente | MCPs existentes permanecem separados; `HOST_DISCOVERED` exige Runtime Doctor |
| ARENA 2.0 | referencia didatica | Licenca ainda nao verificada no manifesto; **nenhuma ativacao** |

## Fornecedores e ambientes independentes

- **JEV/TypeSafe** continua separado de **SponsoredTokens/Laya**: autenticacao, chaves, inferencias, modelos e quotas nao se misturam. A [PR #91](https://github.com/WhiteChronos/ChatGPT/pull/91) ainda e draft.
- **SponsoredTokens/Laya** permanece bloqueado para uso produtivo enquanto os P1 da [Issue #94](https://github.com/WhiteChronos/ChatGPT/issues/94) estiverem sem resolucao verificavel; registrar a saude somente no host Windows real.
- A configuracao `INSTALLED_BY_DEFAULT` no marketplace descreve intencao de empacotamento, nao instalacao nem disponibilidade no Codex Cloud. Nenhuma nova configuracao MCP e adicionada nesta etapa.
- Todos os espelhos em `vendor/` permanecem de leitura. Nao usar o checkout do espelho como runtime de plugin.
- Nenhuma credencial pode ser armazenada neste registro ou enviada de um provedor a outro. Nao realizar testes pagos de inferencia ou instalacoes automaticas.

## Verificacao e gates

O teste canonico executado no CI e:

```bash
python -m pytest -q tests/test_selective_integration_registry.py
python -m pytest -q
```

Esse teste verifica a lista fechada de descritores, as fontes, os estados que **nao** alegam runtime ativado, a origem pelo SHA dos locks, a referencia real das Skills, a politica default-deny e o isolamento dos servicos sensiveis. Atualizar um lock upstream sem atualizar seu descritor causa falha no CI ate revisao explicita. Uma aprovacao de CI nao eleva automaticamente `REGISTERED_PROJECT` para `ACTIVE_RUNTIME_VERIFIED`.

Para provar uso no Codex, executar o Runtime Doctor somente em um checkout limpo do SHA corrente, passando nomes das ferramentas realmente visiveis no host. Registrar no [painel #95](https://github.com/WhiteChronos/ChatGPT/issues/95) o SHA, hostname, JSON e resultado. Para subagentes, `HOST_SUBAGENT_DISCOVERY=PASS` deve anteceder o teste independente de ate dois filhos somente de leitura ja autorizado; IDs e lifecycle sao obrigatorios.

## Ciclo de integracao de novas fontes

1. Evidenciar funcao concreta, repositorio oficial, licenca e SHA de origem.
2. Selecionar escopo minimo e classe de risco; manter referencial/nao executavel por padrao.
3. Adicionar descritor e lock sob controle do fornecedor, sem alterar espelho manualmente.
4. Revalidar testes negativos e positivos, CI, security review e GitHub Arena.
5. Mesclar somente com autorizacao separada do HEAD exato e ruleset Chronos PASS.
6. Habilitar runtime e testar integracoes reais **somente** com aprovacao do ambiente/provedor e evidencias; `RUNTIME_COMPLETE` e `PRODUCTION_COMPLETE` continuam gates separados.

**Roll-back:** reverter a PR de catalogo/politica por um novo PR; nao ha processo de terceiros iniciado por este registro.
