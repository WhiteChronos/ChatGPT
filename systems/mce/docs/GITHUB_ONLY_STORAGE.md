# MCE_INDEPENDENTE — continuidade documental 100% GitHub (contrato de migracao)

Data: 2026-11-10. **Estado: PROPOSTO, NAO IMPLANTADO.** Issue #125, PR #118. O usuario confirmou que nao existe DataCenter Windows local; os caminhos Windows legados sao exemplos contratuais. Este documento nao autoriza alterar arquivos de engenharia, publicar dados privados, provisionar repositorios ou fazer deploy.

## Objetivo e fonte de verdade

- **Codigo publico**: `WhiteChronos/ChatGPT` (PR #118). Apenas codigo, skills, testes sinteticos e decisoes publicaveis, sem arquivos de engenharia, recibos sensiveis, backups, segredos ou bancos.
- **Cofre privado proposto**: `WhiteChronos/mce-document-vault` somente se realmente criado, com visibilidade **private**, acessivel ao conector autorizado e autorizado pelo proprietario para documentos de projeto. A resposta GitHub 404 e `VAULT_NOT_ACCESSIBLE`, nao prova de inexistencia absoluta.
- **Executor**: GitHub Actions `windows-latest`, efemero e acionado sob demanda **no contexto de repositorio privado**. Nao depende de host Windows local; nao assume que o workflow ja exista no cofre.
- **Fontes originais**: documentos enviados conscientemente ao cofre privado, versoes imutaveis e manifests por `project_id/document_id/revision`, com SHA-256 de conteudo e identificadores publicamente nao divulgados.
- **Retomada entre chats**: ler PR #118 e Issue #125 no GitHub; ler os manifests privados **somente** por conector autorizado e com escopo de acesso aprovado. Memoria de chat, titulo de anexo e hash historico nao significam que os bytes foram preservados.

## Fluxo alvo: somente depois da autorizacao e comprovacao do cofre

1. **Preflight fail-closed**: consultar API GitHub do cofre com autenticacao apropriada, confirmar o `full_name`, `private=true`, permissoes minimas, acesso real a branch e protecoes, identificador de projeto e revisao. Se repo nao existir/404/for publico, `BLOCKED` sem ingestao.
2. **Recebimento controlado de bytes**: upload explicito do usuario ao repositorio privado ou interface autenticada autorizada. O conector ChatGPT atual NAO coloca anexos automaticamente no GitHub. Usar arquivo de teste sintetico primeiro; nao escrever dados industriais nesta fase.
3. **Inventario e deduplicacao**: calcular SHA-256 do arquivo antes e depois da gravacao, tamanho, tipo, identidade do documento e revisao. Declarar `ARCHIVED_VERIFIED` apenas depois de leitura real do objeto persistido. Objetos novos jamais sobrescrevem revisoes existentes; conflitos geram nova revisao e decisao humana.
4. **Armazenamento**: arquivos Git privados pequenos podem residir em blobs Git; se necessario Git LFS, conferir limites, cota/custos e acesso a objetos LFS (nao apenas ponteiros). **Nunca** usar cache ou artifacts de Actions como arquivo duravel.
5. **Executor isolado**: workflows Windows no repo PRIVADO, apenas em eventos aprovados (por exemplo, `workflow_dispatch`), tokens `permissions: contents: read` por padrao, elevacao minima apenas na etapa de escrita autorizada, pins de actions por SHA, revisao antes de rodar codigo de PRs externos, sem `pull_request_target` inseguro nem impressao de dados/paths/segredos em logs. O public repo nao deve adquirir acesso generico ao privado.
6. **Recuperacao**: no Windows Actions do privado, restaurar arquivo de teste para nome novo, conferir SHA-256, tamanho e conteudo; registrar recibo em destino privado. Testar erro de revisao, hash incorreto, repo publico, credenciais insuficientes, ausencia de objeto, objeto LFS inacessivel e tentativa de sobrescrever.
7. **Integridade e imutabilidade**: protecao de branch/tag, `CODEOWNERS`, protecao contra force-push/delecao, revisao, trilha de auditoria, retencao/versionamento e verificacao periodica. `private` nao significa criptografia ponta-a-ponta ou imutabilidade absoluta.
8. **Recuperacao de desastre**: segundo repositorio GitHub privado pode prover redundancia logica, mas **nao** independencia de plataforma/conta. Se o usuario insistir em GitHub-only, declarar explicitamente esse risco residual e nao alegar `INDEPENDENT_BACKUP_VERIFIED`. Para recuperacao apos comprometimento total de conta, exigir copia de dominio independente, quando aprovada.

## Gate MCE de engenharia (inalterado)

O motor de engenharia existente permanece unico. Antes de editar XLSX: projeto/SS documentados, modelo mestre P09 homologado, inventario MD/ET/P&ID/I/O e SHA, whitelist exata de celulas, autorizacao externa vinculada aos hashes e `AUTORIZO_ELABORACAO_MCE`, copia derivada, verificacao OOXML e revisao multidisciplinar. Nenhum workflow cloud pode conceder autoaprovacao nem inferir setpoints, alarmes, trips ou logica de seguranca. Para ADM GAMBOA, o SHA de memoria historica e apenas indicador; restauracao real continua `NOT_VERIFIED` ate encontro dos bytes e validacao.

## Gates de aceite verificaveis

| Gate | Evidencia requerida | Estado na definicao |
| --- | --- | --- |
| GH-01 | Repositorio privado dedicado realmente acessivel e permissao aprovada | BLOCKED |
| GH-02 | Acesso minimo, protecao, politica de privacidade/custos e revisao | NOT_VERIFIED |
| GH-03 | Upload sintetico autorizado e recibo SHA-256 persistente | NOT_RUN |
| GH-04 | Workflow Windows privado acionado e concluido em SHA exato | NOT_RUN |
| GH-05 | Restore sintetico com mesmo SHA (incluindo perda de copia primaria) | NOT_RUN |
| GH-06 | Acesso ChatGPT autorizado a objetos privados sem exposicao em repo publico | NOT_VERIFIED |
| GH-07 | Redundancia e retencao comprovadas; risco de falha comum explicitado | NOT_VERIFIED |
| GH-08 | Reencontro da MCE ADM original e revisao de engenharia (se disponivel) | BLOCKED |

Nao declarar `PRODUCTION_COMPLETE=YES` pela CI do repositorio publico. Nem merge, criacao de cofres, custos, segredos, upload real ou implantacao sem autorizacao e interfaces apropriadas.

## Referencias oficiais

- GitHub Actions hosted runners: https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners
- Permissoes do GITHUB_TOKEN: https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication
- Git LFS: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage
- Actions artifacts e retencao: https://docs.github.com/en/actions/managing-workflow-runs/downloading-workflow-artifacts
- Referencia interna: `systems/mce/AGENTS.md`, `systems/mce/spec/memoria.md`, `systems/mce/docs/DATACENTER_MEMORY.md`, Issue #125.

## Ferramenta GH-01 implementada no repositorio publico (somente metadados)

O script `systems/mce/scripts/github_vault_preflight.py` pode ser executado com **Python 3.12+ em GitHub Actions Windows** depois que o repositorio privado tiver sido criado e aprovado. Nao e mecanismo de armazenamento, nao utiliza Windows local, nao instala dependencias e nunca recebe bytes industriais. O operador/workflow privado fornece o token temporario via variavel de ambiente `MCE_VAULT_GITHUB_TOKEN`, com permissoes minimas suficientes. A API exige o nome exato do repositorio, `private=true`, `permissions.push=true` e `default_branch` nao vazio. Resposta PASS indica apenas que o destino privado esta acessivel para possivel ingestao; NAO prova upload, criptografia, backup ou restauração.

Exemplo para workflow privado autorizado (nao colar token em argumentos/linha de comando/logs):

```powershell
python .\\systems\\mce\\scripts\\github_vault_preflight.py --repo WhiteChronos/mce-document-vault
```

Variavel no step do workflow privado: `MCE_VAULT_GITHUB_TOKEN: ${{ github.token }}`. O script retorna exit code 2 em bloqueio e apenas JSON sanitizado. Um token apenas de leitura pode retornar `NO_WRITE_PERMISSION`, **sem** induzir ampliacao automatica de privilegios. Nunca executar teste privado na CI do repositorio publico com tokens do cofre.

**Validacao CI publica:** os testes sintéticos no Windows em `systems/mce/tests/test_github_vault_preflight.py` verificam metadata publica/incorreta, token ausente, identificador invalido, 404 e excecao contaminada por texto de segredo. Eles nao provam GH-01 no vault real. Depois do provisionamento e aprovacao humanos, executar este script no runner **do repositorio privado** e anexar o link de run ao gate GH-01.
