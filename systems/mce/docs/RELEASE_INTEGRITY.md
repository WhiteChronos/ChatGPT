# MCE independente — verificador de integridade do release

MCE e um workflow offline de engenharia; nenhuma implantacao de servidor MCP ou Web e requisito de producao. O novo `scripts/release_integrity.py` examina um ZIP fechado, **sem extrair arquivos**, sem sobrescrever a matriz mestre, sem copiar desenhos e sem executar macros. Compara o conteudo byte a byte com `manifest.json` SHA-256, rejeita membros extras, caminhos de travessia, duplicatas, links simbolicos e ZIPs excessivamente grandes.

Uso:

```bash
python scripts/release_integrity.py --zip /CAMINHO/CANDIDATO_PREPRODUCAO_MCE_INDEPENDENTE.zip --expected-sha256 SHA256_FORNECIDO_FORA_DO_ZIP --expected-git-sha COMMIT40_CONFIRMADO_NO_GITHUB
```

**Exit 0 e `INTEGRITY_PASS`** provam somente identidade de bytes do pacote revisado: o operador precisa comprovar origem autorizada do ZIP/manifesto, assinatura ou checksum publicado no GitHub aprovado, aprovacao do PR e permissao do host real.

**Exit 2 e `BLOCKED`** impedem instalar o release: substituir o pacote pela versao autentica. Nunca corrigir manualmente um manifesto, instalar um arquivo com bytes desconhecidos ou renomear um ZIP corrompido para passar.

Mesmo com integridade PASS, permanecem exigidos o codigo versionado e aprovado, fontes oficiais do projeto, Excel mestre aprovado, limite de 50 causas por folha, revisao de Processo/Instrumentacao/Automacao/Seguranca quando aplicavel, auditoria OOXML, FAT/SAT e assinatura do responsavel. O verificador imprime `production_complete=false` e **nao** altera a matriz.

## Prova externa separada do manifesto

O verificador agora oferece `--expected-sha256` para comparar a **totalidade do ZIP** com um SHA-256 publicado em um canal confiavel independente do arquivo recebido, e `--expected-git-sha` para comparar o commit alegado no manifesto com o commit revisado no GitHub. Um checksum copiado do proprio ZIP, de uma fonte nao confiavel, nao prova autenticidade de origem.

`trusted_digest_match=true` e `trusted_commit_match=true` significam correspondencia de bytes a **valores informados pelo operador**, nao homologacao, revisao humana ou assinatura digital. O campo `production_complete` permanece `false`. Ambos os parametros sao opcionais para compatibilidade com a auditoria anterior; para aceite de release operacional, a organizacao deve exigir os dois valores de fonte confiavel. Com mismatch ou SHA malformado: `BLOCKED` e exit code 2.
