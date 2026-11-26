---
name: mce-verificador-efeitos-x
description: Auditoria independente, somente leitura, de cobertura de cruzamentos X e efeitos de cada Equipamento / Serviço / Zona em Matriz de Causa e Efeito industrial Excel P09, inclusive ADM Gamboa. Detecta causas sem X, X sem titulo de efeito, efeitos sem uso, perdas entre revisoes e falta de evidencia individual. Bloqueia entrega sem cobertura; nunca inventa X nem exclui linhas.
---

# Verificador de efeitos X - cobertura obrigatoria

## Entrada obrigatoria
- XLSX da MCE do projeto (abas `FOLHA N`); referencia anterior opcional para controle de perdas.
- Perfil `adm-gamboa-40` (linhas 8:47, reservado exclusivamente ao ADM) ou `p09-50` (8:57, padrao para Area Externa).
- Ledger de evidencias opcional, com uma prova por cruzamento. A falta de ledger **nao valida o X**; apenas permite inventario visual.
- Fontes aprovadas com revisão e SHA para afirmacoes funcionais; nunca confundir arquitetura com filosofia de controle.

## Resultado e regra de bloqueio
1. Conferir cada linha com `C` (Equipamento / Serviço / Zona), `F` (TAG) ou `H` (indice). `C7` e o cabecalho, **nao e causa**.
2. Em cada causa, percorrer I:AQ (35 posicoes). Um `X` somente e contado se houver titulo de efeito real na linha 5 da mesma coluna. Outros caracteres sao sinalizados; nao converter automaticamente.
3. Toda causa deve ter **pelo menos um X validamente localizado**. Se nenhuma relacao existir: `CAUSA_SEM_X` e `BLOCKED`. A causa continua no arquivo para avaliacao do engenheiro; jamais a remover para melhorar a taxa.
4. Toda coluna de efeito com titulo real deve ser avaliada. Se nenhum X tiver sido localizado, informar `EFEITO_SEM_X`; titulo repetido em outra folha nao autoriza clonar X.
5. Conferir se cada X tem claim aprovado no ledger (folha, celula, indice H, TAG, documento, SHA, revisao, trecho/posicao e aprovacao). Sem prova, registrar `X_SEM_EVIDENCIA_APROVADA`. Mesmo que toda linha tenha X, nao declarar cobertura funcional completa.
6. Com baseline, detectar perda de causas/TAG, folha e X. X novo nao e automaticamente incorreto: permitir quando a mesma celula, indice, TAG e efeito constarem no ledger com `status=APROVADO`, aprovador, fonte e SHA; sem essa evidencia, emitir `X_ADICIONADO_SEM_APROVACAO`. Nunca aplicar automaticamente.
7. Nao aceitar `NAO_APLICAVEL` implicitamente para evitar X. Se um equipamento nao gera efeito na MCE, requer decisao formal de escopo/documento, nao preenchimento ficticio.
8. A auditoria so pode retornar `PASS_ESTRUTURAL_COM_EVIDENCIAS` quando todos os X possuem ledger individual aprovado, nenhuma causa esta sem X e nao ha erros. Esse PASS nao significa homologacao, QA Windows ou aceite multidisciplinar. Nesses casos o resultado definitivo pertence ao gate `mce_delivery_contract.py` e ao executor MCE, nao a esta skill.
9. Preservar os originais, o perfil de 40 posicoes e os 3 conjuntos de causas aprovados; esta skill NUNCA escreve XLSX. Para editar, encaminhar ao executor canonico `engenharia-mce-projeto/scripts/mce_workflow.py` com whitelist e gates humanos.
10. Respeitar SDAI/SPCI como interfaces de supervisao documentadas; nao inventar trips, comandos, SIF ou logicade intertravamento. H2 somente evento recebido via SDAI/SCADA no ADM.

## Execucao
```bash
python scripts/verificar_efeitos_x.py --workbook MCE.xlsx --profile p09-50 --expected-causes 60 --ledger evidencias_aprovadas.json --output auditoria.json --fail-on-missing
python -m unittest discover -s tests -v
```
Opcional: `--baseline MCE_ANTERIOR.xlsx`. O ledger deve conter `approved_relations` com prova individual; sem ledger, um X visual nao constitui X aprovado. `--expected-causes` compara o inventario esperado com as causas reais. A matriz sem X deve falhar com `MATRIZ_SEM_X`. Usar `--allow-unused-effect-columns` apenas com decisao formal de nao aplicabilidade e sem afirmar homologacao. O script emite JSON por folha/celula e jamais edita Excel. Para entrega, exigir ainda `systems/mce/scripts/mce_delivery_contract.py` e `systems/mce/scripts/mce_delivery_guard.py`, na PR #139, com exit code zero. Em falha, `MCE_XLSX=NAO_EMITIDO_BLOQUEADO`. Usar `references/criterios.md`.

## Arena e Superpowers
- Fazer revisao por quatro perspectivas: (1) fonte/evidencia, (2) limites e identidade, (3) regressao/adversarial, (4) manutenibilidade.
- Quando o plugin oficial Superpowers estiver realmente disponivel: `using-superpowers` -> `systematic-debugging`/`test-driven-development` -> `verification-before-completion`.
- Sem plugin oficial, aplicar testes deterministas e registrar `SUPERPOWERS_OFICIAL=NAO_EXECUTADO`; nao declarar agente independente nem ativacao universal.
- Executar teste real: arquivo ADM com 91 causas, 19 sem X, incluindo `FOLHA 2!C7` que e um cabecalho; resultado obrigatorio `BLOCKED`.
- Documento da arquitetura para o campo Fluxograma: `DE-2713.01-6613-869-RPJ-006` sem `=D`; referencia nao valida X.

## Saida
- `auditoria_efeitos_x.json` e lista de pendencias. Sem cobertura e provas = nao homologado. Nao marcar 100% baseado apenas em contagem.

## Regressao obrigatoria em MCE
- Validar `python -m unittest discover -s tests -v` antes da publicacao. Um X novo aprovado deve passar; um X novo pendente deve bloquear.
- Conferir hash do Excel original antes/depois. Nunca alterar o mestre ou copiar X entre ADM e Area Externa.
- Nao usar somente o numero declarado em JSON: contar X reais nas celulas I:AQ e comparar os totais com o contrato de entrega.
- Registar a alteracao no GitHub junto da memoria e manter o catalogo instalado separado da branch ate aprovacao e instalacao efetiva.