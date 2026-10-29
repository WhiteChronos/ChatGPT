# REA independente — operacao em producao e MCP no ChatGPT Web

## Arquitetura recomendada

O REA interno e um motor estatico read-only distinto do projeto oficial `morluto/rea`. Nao tem dependencia de MCE, planilhas, P&ID ou controle de matriz. O servidor atual e a UI Web estao limitados a loopback. Isto e intencional: **nao publicar o processo Python cru diretamente na Internet**.

Evolucao de producao proposta: operador escolhe **host de containers/VM sob seu controle**, executa o motor interno com usuario sem privilegios, dados autorizados em volume restrito, porta somente localhost, HTTPS em proxy com autenticacao robusta (idealmente SSO/OAuth), politicas de acesso/ingress, limites, logs sem segredos e rotacao de credenciais. Implantacao, credenciais, DNS e custos exigem autorizacao separada. Nao assumir que paginas estaticas ou Vercel serverless sejam substitutos validos de um MCP persistente com filesystem local.

## Estrategias Arena

| Alternativa | Efeito | Decisao |
| --- | --- | --- |
| Expor `0.0.0.0:8768` sem proxy | Dados privados e token sob risco | PROIBIDO |
| Hospedar UI estatica sem backend | Nao executa MCP ou analise de codigo | DESCARTADO |
| Túnel temporario autenticado para ensaio | Util para canary isolado com aprovacao e revogacao | CONDICIONAL |
| Host gerenciado + TLS + identidade + logs + rollback | Operacao robusta com dominio e provas reais | RECOMENDADO |

## Smoke de endpoint HTTPS — nao equivale a host descoberto

Apenas **depois** que um operador autorizar e configurar o endereco HTTPS real e as credenciais, executar:

```bash
python -m pip install -r systems/rea/requirements.txt
python -m pytest -q systems/rea/tests
export REA_MCP_TOKEN='TOKEN_DE_OPERADOR_NAO_COMMITAR'
python systems/rea/scripts/production_smoke.py --url https://rea.sua-organizacao.example/mcp
```

O comando verifica esquema `https`, recusa URL com senha ou query, nao aceita redirecionamentos, valida certificado via cliente HTTPS padrao, testa HTTP 401/403 sem token, faz JSON-RPC `initialize`, `tools/list` com as **sete** ferramentas internas, e uma chamada segura `rea_bridge_status`. Saida: `ENDPOINT_SMOKE_PASS` apenas se o endpoint responder; nao imprime o token nem le arquivos de projeto. Sem URL ou token, `BLOCKED`, exit code 2. Testes com servidor simulado nao equivalem ao smoke de um endpoint real.

**Atenção:** o desafio de seguranca com token nao substitui identidade individual, OAuth adequado, isolamento multiusuario, controle de acesso por escopo, auditoria e avaliacao de protecao de dados. Essas caracteristicas nao estao comprovadas nesta versao e precisam ser validadas antes de abertura externa.

## Gates para producao integral

| Gate | Evidencia e responsavel | Sem evidencia |
| --- | --- | --- |
| Commit incorporado e CI | SHA `main`, PR, testes e checks (mantenedor) | BLOCKED |
| Runtime instalado no host | versoes de Python e deps, registro de processo e usuario nao privilegiado (operador) | BLOCKED |
| Endpoint protegido | DNS, HTTPS/TLS valido, proxy/SSO, access-control e segredo gerenciado (DevSecOps) | BLOCKED |
| Suite adversarial | caminhos externos, symlinks, arquivos sensiveis, request size, token falso, CORS e rate limits (QA/Sec) | BLOCKED |
| Smoke no endereco definitivo | URL e logs com `ENDPOINT_SMOKE_PASS` do HTTPS real (operador) | BLOCKED |
| Descoberta no ChatGPT Web | `tools/list` observado **pelo host conectado** com origem e permissao reais (operador/usuario) | BLOCKED |
| Aceite e operacao | politica de disponibilidade, logs sanitizados, observabilidade, rollback e aprovacao (proprietario) | BLOCKED |

**Importante:** verificar o endpoint externamente nao prova que o ChatGPT Web descobriu as ferramentas. A ativacao exige cadastro da integracao no cliente e validacao do inventario naquele host. O REA oficial `rea-agents` e outro produto; sua propria ativacao precisa de processo de instalacao e evidencia separados.

## Plano Superpowers para fechar gates

1. Revisar e integrar PR com checks e revisao em SHA vigente (sem bypass).
2. Selecionar provedor, modelo de acesso, fontes permitidas, custo e responsavel; aprovar arquitetura de dados e seguranca. **STOP** sem escopo e dono.
3. Executar canary privado em host isolado com TLS e credenciais gerenciadas; adicionar monitoramento e rollback.
4. Rodar smoke externo e ataques negativos; manter prova com SHA da imagem/commit e data.
5. Configurar MCP no ChatGPT Web somente com aprovacao do operador; verificar `tools/list` real, chamada segura read-only e revogacao de acesso.
6. Promover canary a stable somente com verificacoes, aprovacao de operacao e caminho de rollback documentado.
