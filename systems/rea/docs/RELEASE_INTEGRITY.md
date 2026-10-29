# REA — verificacao do release independente

## Escopo

O verificador `scripts/release_integrity.py` calcula o SHA-256 do ZIP completo, confere todos os hashes dos membros contra `manifest.json`, verifica a identidade `REA_INDEPENDENTE`, o SHA Git e bloqueia a existencia de arquivos extras, colisao de nomes, links simbolicos, caminhos de travessia e arquivos acima de limites. Tudo **sem extrair ou executar** o conteudo. Nao importa nada do MCE.

## Como usar

```bash
python scripts/release_integrity.py --zip /CAMINHO/RELEASE_REA.zip --expected-sha256 SHA256_DO_RELEASE_EM_CANAL_CONFIAVEL --expected-git-sha COMMIT40_VALIDADO_NO_GITHUB
```

`INTEGRITY_PASS` com `trusted_digest_match=true` e `trusted_commit_match=true` significa que a evidência local corresponde aos valores informados externamente. Nao significa que o autor tenha assinado o ZIP, nem que o PR foi aprovado, que o codigo foi implantado, que o host esta seguro ou que o plugin MCP foi conectado. A declaracao `production_complete` e sempre `false`.

Sem valores externos, a verificacao continua util para detectar dano de transporte, mas **nao comprova autenticidade**. Sem canal aprovado, a operacao deve continuar bloqueada. Divergencias, SHA invalido ou ZIP inseguro devolvem exit code 2 e `BLOCKED`.

## Gates humanos e operacionais remanescentes

O operador precisa confirmar o artefato no release GitHub autorizado, instalar no host com acesso restrito, concluir o Secure MCP Tunnel, realizar `tunnel-client doctor` e uma chamada read-only real no ChatGPT Web, revisar monitoramento/rollback, obter aceite operacional e de seguranca. Veja `docs/PRIVATE_MCP_TUNNEL.md` e `docs/PRODUCTION_ACCEPTANCE.md`.
