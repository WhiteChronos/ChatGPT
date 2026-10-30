# MCE privado no Codex e ChatGPT

O adaptador `scripts/mce_sdk_server.py` executa somente em Windows nativo
(PowerShell, Python 3.12+) e oferece sete ferramentas stdio pelo SDK
oficial. Reutiliza o workflow canônico; MCP é dependência **opcional**, não do
motor local. Instalar `requirements-web.txt` somente no ambiente MCE isolado.

## Diretórios e execução

Preparar fora do checkout uma pasta autorizada contendo `inbox/` e `projects/`.
Criar outra pasta externa para aprovações. O servidor recebe somente chave
**pública Ed25519** de um operador, nunca a privada. Sem chave pública, consulta e
entendimento funcionam, mas elaboração permanece bloqueada.

```text
python scripts/mce_sdk_server.py --root C:\MCE_DADOS\Autorizado --approvals C:\MCE_DADOS\Aprovacoes --public-key C:\MCE_CHAVES\operador-publico.pem
```

Usar stdio local ou túnel privado separado e aprovado. O adaptador não abre porta
HTTP, cria túnel, publica documentos nem importa anexos de conversas.
Arquivos precisam ser transferidos para inbox com autorização específica.
Credenciais do transporte não fazem parte do pacote nem aprovam engenharia.

## Operações

| Ferramenta | Efeito |
| --- | --- |
| mce_status | Identidade, cinco skills e limites de aprovação |
| mce_read_skill | Consulta uma skill canônica pelo nome |
| mce_inspect_model | Inventário e SHA de XLSX autorizado; não aprova modelo |
| mce_initialize | Cria baseline nova e preserva originais |
| mce_understand | Registra análise/contrato revisados e para aguardando decisão |
| mce_approval_request | Hashes exatos para revisão externa, sem autorizar |
| mce_apply | Exige assinatura externa válida e gera job/cópia preliminar auditada |

As três operações de criação têm read_only_hint=false e não são idempotentes.
Não existe ferramenta authorize, shell, assinador remoto ou gravação arbitrária.
A entrada de engenharia continua sendo matriz-causa-efeito, com seus três
adaptadores, DataSheet e SQLite já existentes. mce-operacao-web só rege transporte.

## Aprovação humana externa

O operador obtém a solicitação de mce_approval_request, confere os documentos,
modelo e diferenças **reais**, projeto/SS e whitelist. A assinatura aprova o
modelo e o contrato exatos, não autentica a correção de uma lógica industrial.
O responsável precisa controlar a chave privada fora da raiz remota, em volume
privado protegido. Uma assinatura sintética de teste não é aprovação humana.

O CLI `scripts/mce_operator_approval.py` exige request, private-key, authorized-root,
output externo, approver, `--decision AUTORIZO_ELABORACAO_MCE` e `--model-reviewed`.
A validade padrão é uma hora, limitada a 24 horas. A API recebe apenas nome do
arquivo de aprovação na pasta externa configurada; não aceita texto "aprovado".

Alterações no modelo, fontes, estado, análise, contrato ou mudanças invalidam a
assinatura. A tentativa consome a solicitação antes de rodar; falhas exigem nova
revisão. Uma cópia congelada em `jobs/<id>/` é usada na aplicação para impedir
troca de entradas depois da verificação. A baseline continua inalterada.

## Proteções e limites

Bloqueiam-se travessia, nomes ocultos, links, hardlinks, reparse points, macros,
XML com entidades, ZIPs/JSON grandes, membros repetidos e dimensões excessivas.
Limites: arquivo 20 MiB; membro XML/ZIP 4 MiB; ZIP expandido 50 MiB/256 membros;
workbook 200 mil células dimensionadas, 20 mil linhas e 256 colunas por folha;
workspace 300 arquivos/100 MiB. Isso é limite de recurso, não liberação industrial.

Os controles da interface assumem host privado sem operador malicioso com acesso
administrativo. Não são isolamento do sistema operacional. Exigir ACL/criptografia,
gestão de chaves, acesso ao túnel e aprovação de transferência antes de dados reais.

O editor existente mantém <=50 causas por folha, texto em cinza, fórmulas e partes
OOXML preservadas. Saída: MCE_PRELIMINAR_PARA_REVISAO, nunca homologação automática.
Revisão multidisciplinar, FAT/SAT aplicável, rollback e aceite seguem externos.
Instalação, SDK local, descoberta no host e chamada ChatGPT são evidências distintas.
