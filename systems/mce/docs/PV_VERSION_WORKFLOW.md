# MCE_INDEPENDENTE - ciclo documental PV e validacao integrada
Data da regra: 2026-11-11. Decisao publica DEC-MCE-078. Este arquivo registra PROCESSO e nao contem arquivos, TAGs, trechos ou memoria industrial privada.

## 1. Nome e identidade
Nome exato: NOME_DO_DOCUMENTO + espaco + (PRELIMINAR VERSAO NN) PV NN + extensao .xlsx.
O texto grafado no arquivo deve usar acento portugues: PRELIMINAR VERSÃO.
Exemplo sintetico: MCE_TESTE (PRELIMINAR VERSÃO 01) PV 01.xlsx.
PV 02, PV 03 e seguintes sao sequenciais POR DOCUMENTO; cada novo documento com identidade propria inicia em PV 01.
Nao reutilizar numero, nao sobrescrever, nao promover PV a revisao aprovada.
A regra se aplica tambem ao nome do PDF espelho, quando requisitado, com mesma raiz e mesmo PV.
Anexos de auditoria sao AUXILIARES, nunca arquivo principal da matriz.

## 2. Ordem canonica
1. Recuperar memoria MCE (memoria.md, Issue #120 e status real da PR/SHA), documentos e fontes sob escopo autorizado; consultar system-memory/index.json se acessivel. Caso contrario registrar NAO_ACESSIVEL; memoria nao autoriza mudanca.
2. Inventariar projeto, SS, codigo do documento, revisoes ET/MD/Arquitetura/P&ID/I/O, hashes de cada fonte e modelo P09 aprovado. Nao presumir cofre/Windows local instalado.
3. Executar a skill mce-verificacao-cruzamentos: revisar todas as 35 posicoes de efeitos por folha, X existentes, causas com/sem X, repeticoes e efeito nao aplicavel justificado. NUNCA preencher X por contagem ou para evitar coluna vazia.
4. Executar mce-verificacao-documental: confrontar fontes e trechos com TAG, evento, condicao, tipo de sinal, causa H, coluna/efeito e coordenada; validar revision/SHA. Esquema de handoff: added_relations apenas X JA EXISTENTES, candidate_relations nunca pre-aprovados. Reexecutar a skill de cruzamentos com ledger documental.
5. Resolver contradicoes MD/ET/Arquitetura por responsavel; diferenciar topologia e supervisao de comando hardwired, logica de CLP, SIS/F&G e permissivos. Na falta de prova, PENDENTE, sem inventar.
6. Preparar contrato candidato com mce_workflow.py propose-contract, depois revisar e aprovar whitelist e modelo homologado; nao repetir solicitacao geral de trabalho ja recebida, mas nao fingir aceite tecnico.
7. Somente com gates, executor MCE canonico faz authorize, apply --changes e audit sobre copia derivada. Nao editar XLSX pelas skills de auditoria. Testar preservacao P09, formulas, mesclas, X historicos, observacoes, SP, legendas, 35 posicoes de efeitos e SHA/OOXML.
8. Se houver XLSX derivado valido, executar mce_pv_controller.py no root PRIVADO: --source relativo --document-name SEM SUFIXO PV --sha256 da fonte. O comando copia bytes para pv/<documento> (PRELIMINAR VERSÃO NN) PV NN.xlsx e anexa uma entrada encadeada em pv/pv_versions.jsonl. O mesmo SHA nao cria outra PV do mesmo documento. Conferir XLSX/PDF pelo mce_delivery_contract.py antes de declarar entrega tecnica.
9. Gerar relatorio de pendencias separado, nunca abas CONTROLE ou AUDITORIA na MCE P09. Status MCE_PRELIMINAR_PARA_REVISAO sem homologacao automatica.
10. Apos compatibilizacao, aprovacao multidisciplinar, QA Excel Windows, requisitos de teste e aceite, registrar evento EXTERNO de fechamento. A PV permanece historica; o documento final segue codigo/revisao aprovados, sem renomear PV como final automaticamente. Proximo documento: nova identidade, ledger proprio, PV 01.

## 3. DataCenter, memoria e continuidade
- Fonte de codigo e decisoes publicaveis: WhiteChronos/ChatGPT, memoria MCE e Issue #120. Usar o mesmo commit para codigo, skills MCE ja publicas e memoria; PR/CI por SHA. Sem merge/deploy automatico.
- Registro privado de PV: manifesto append-only em workspace autorizado com nome, sequencia, SHA de origem/destino, digest encadeado, data e status. O encadeamento detecta mudancas, nao autentica aprovador.
- O unico ledger MCE de memoria operacional continua memory_events de datacenter/schema.sql. Quando houver host real autorizado, registrar evento NOTE ou STATUS com subject MCE_PV_VERSION, document ID, PV, SHA e ID de decisao; nao criar um segundo banco.
- A memoria MCE em Git e apenas metadata de workflow, nunca textos industriais, listas I/O ou arquivos XLSX. O DataCenter Windows local foi declarado INEXISTENTE; alvo GitHub-only com cofre privado depende de acesso e ingestao verificados. Nao prometer sincronizacao nem arquivamento nao comprovado.
- Aprendizado continuo = identificar defeito verificavel -> evento de licao -> teste de regressao -> proposta de regra/Skill -> revisao humana -> commit/CI/medicao comparavel -> revisao. Nenhum agente modifica regras, pesa modelo, homologacao ou Excel sozinho.
- Integracao com as skills novas: quando realmente descobertas no host, invocar mce-verificacao-cruzamentos e mce-verificacao-documental com handoff JSON. Seus arquivos privados nao sao distribuidos por este repositorio publico sem autorizacao explicita. Usar o pacote privado aprovado como fonte, nunca placeholder.

## 4. Controles negativos e limites
- Documento com nome generico MCE_PRELIMINAR.xlsx e invalido como ENTREGA nova; pode continuar arquivo tecnico intermediario interno.
- Rejeitar PV com numero divergente no parentese e no sufixo, PV 00, salto PV, mesmo SHA sem alteracao, path traversal, symlinks, overwrites e ledger adulterado.
- Nao usar 9/9 CI como evidencia de edicao real, revisao funcional completa, DataCenter ativo ou producao. Nao passar P09 visual sem QA no Excel Windows.
- Nas matrizes ainda em revisao, coluna sem X pode ser nao aplicavel ou repeticao; exigir justificativa, jamais inventar.
- Para liberar formalmente, fontes, I/O, documento/aprovacao e QA continuam gates externos; quando ausentes MCE_XLSX=NAO_EMITIDO_BLOQUEADO para EMISSAO FORMAL.

## 5. Evidencia e testes
Fonte de verdade: systems/mce/scripts/mce_pv_controller.py, systems/mce/scripts/mce_delivery_contract.py e respectivas suites sinteticas. Auditoria independente usa arquivos privados so em escopo autorizado. O recibo PV nao concede permissao para editar dados ou executar conteudo de fonte.
