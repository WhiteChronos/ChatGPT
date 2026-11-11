# MCE independente — aceite para producao (sem alterar o Excel mestre)

## Definicao de producao

O MCE e um sistema local de engenharia de causa e efeito, nao uma API publica. Producao significa a **execucao da versao aprovada** no ambiente de engenharia autorizado, sobre um modelo mestre realmente aprovado, com fontes oficiais rastreaveis, aceite multidisciplinar e evidencias FAT/SAT quando aplicavel. Nao confundir testes sinteticos/CI com homologacao operacional.

O codigo deste produto nao depende de um servidor de engenharia reversa, de publicacao Web ou de credenciais de nuvem.

## Estrategias avaliadas (Arena + Superpowers)

- **Publicar um servico Web de edicao automatica:** rejeitado. Introduz acesso e alteracao do modelo sem gates humanos e descaracteriza o contrato Excel.
- **Tratar a CI verde como liberacao:** rejeitado. Nao verifica o modelo real, as revisoes e aprovacao das disciplinas.
- **Fluxo offline de release imutavel + gates documentais e humanos:** recomendado. Preserva a matriz mestre, a rastreabilidade e a operacao dentro do ambiente autorizado.
- **Executar geracao de MCE diretamente em producao sem projeto/SS:** proibido. A ferramenta deve bloquear antes do aceite.

## Teste tecnico local (somente leitura)

```bash
python -m pip install -r systems/mce/requirements.txt
python -m pytest -q systems/mce/tests
python systems/mce/scripts/production_readiness.py --workspace /PROJETO_MCE_AUTORIZADO
```

O verificador nao escreve no workbook ou em arquivos de estado. Ele repete a checagem de SHA-256 do modelo e das fontes, a identificacao documental projeto/SS, as restricoes do contrato de ate 50 causas/folha, o registro de autorizacao, o SHA da saida e a auditoria OOXML independente. Sem todos esses itens, retorna exit code 2 e `BLOCKED`. Quando os gates tecnicos locais estao satisfeitos, retorna `TECHNICAL_READY_FOR_ENGINEERING_ACCEPTANCE`; **jamais declara `production_complete=true`**.

## Gates restantes para 100% de aceite operacional

| Gate | Fonte de prova exigida | Responsavel | Sem evidencia |
| --- | --- | --- | --- |
| Codigo final incorporado | SHA de `main` + PR revisado + CI desse SHA | Mantenedor GitHub | BLOCKED |
| Release reproduzivel | artefato e manifesto SHA-256 aprovados | Mantenedor | BLOCKED |
| Ambiente operacional | Python e dependencias instalados, checksum e permissao testados no host real | Operador MCE | BLOCKED |
| Projeto, SS e documentos reais | fontes oficiais aprovadas, versoes, localizacao e inventario hash | Engenharia | BLOCKED |
| Modelo Excel mestre | identificacao e aceite documental do modelo, whitelist, maximo de 50 causas por folha | Responsavel do modelo | BLOCKED |
| Autorizacao humana | registro externo confiavel, identidade do aprovador e SHA das fontes | Responsavel tecnico | BLOCKED |
| Matriz derivada | auditoria OOXML, validacao visual, formulas, legendas e cabecalhos intactos | Eng. Automacao | BLOCKED |
| Revisao multidisciplinar | pareceres de Processo, Instrumentacao, Automacao, Operacao e Seguranca quando aplicavel | Lideranca de engenharia | BLOCKED |
| FAT/SAT e retorno | resultados reais onde requeridos, estrategia de rollback para a revisao anterior | Operacao/Comissionamento | BLOCKED |

`PRODUCTION_COMPLETE` so pode ser emitido por governanca operacional apos **todos** os gates, no projeto real, validados contra evidencia independente. O verificador automatico nao assina aceitacoes nem transforma resultados preliminares em aprovados.

## Plano de implementacao e fechamento (Superpowers)

1. Revisar e integrar o PR com SHA vigente, com controles Chronos, revisao e CI integral. **STOP** se SHA/checks divergirem.
2. Gerar pacote versionado e hash no ambiente de build; ensaiar instalacao limpa em host alvo, sem fontes confidenciais no repositorio publico.
3. Validar um projeto autorizado, seus documentos e o contrato Excel; executar o verificador somente-leitura; documentar pendencias.
4. Obter expressamente autorizacao para preencher, executar `authorize`, `apply`, `audit`, conferir diff/semantica/cinzas e colher revisoes humanas.
5. Executar FAT/SAT quando definidos, registrar aceite e um procedimento de retorno para o artefato anterior. **STOP** sem aprovacao humana para a liberacao.

## Riscos adversariais

- Manipular `state.json` ou simular o nome de um aprovador nao constitui assinatura: exige fonte externa de confianca.
- O hash de um arquivo nao verifica a validade tecnica da logica/seguranca.
- CI verde em dados sinteticos nao prova semantica P&ID, SIF ou equivalencia visual de todos os recursos Excel.
- O arquivo `.xlsx` mestre nunca deve ser sobrescrito pelo workflow ou colocado em repositório publico por padrao.
