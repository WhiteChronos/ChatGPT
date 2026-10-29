# MCE independente — verificador de integridade do release

MCE e um workflow offline de engenharia; nenhuma implantacao de servidor MCP ou Web e requisito de producao. O novo `scripts/release_integrity.py` examina um ZIP fechado, **sem extrair arquivos**, sem sobrescrever a matriz mestre, sem copiar desenhos e sem executar macros. Compara o conteudo byte a byte com `manifest.json` SHA-256, rejeita membros extras, caminhos de travessia, duplicatas, links simbolicos e ZIPs excessivamente grandes.

Uso:

```bash
python scripts/release_integrity.py --zip /CAMINHO/CANDIDATO_PREPRODUCAO_MCE_INDEPENDENTE.zip
```

**Exit 0 e `INTEGRITY_PASS`** provam somente identidade de bytes do pacote revisado: o operador precisa comprovar origem autorizada do ZIP/manifesto, assinatura ou checksum publicado no GitHub aprovado, aprovacao do PR e permissao do host real.

**Exit 2 e `BLOCKED`** impedem instalar o release: substituir o pacote pela versao autentica. Nunca corrigir manualmente um manifesto, instalar um arquivo com bytes desconhecidos ou renomear um ZIP corrompido para passar.

Mesmo com integridade PASS, permanecem exigidos o codigo versionado e aprovado, fontes oficiais do projeto, Excel mestre aprovado, limite de 50 causas por folha, revisao de Processo/Instrumentacao/Automacao/Seguranca quando aplicavel, auditoria OOXML, FAT/SAT e assinatura do responsavel. O verificador imprime `production_complete=false` e **nao** altera a matriz.
