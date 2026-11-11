# PROMPT-MESTRE — GLOSSÁRIO P&ID / AUTOMAÇÃO BASEADO EM GITHUB v1.0

## Objetivo
Criar e manter um glossário técnico data-centric de P&ID, instrumentação, automação, processo, tubulação, elétrica correlata, HVAC, SIS/ESD/F&G e SDAI, usando GitHub como fonte secundária de software, modelos de dados, bibliotecas abertas, exemplos e mecanismos de validação.

## Regra de autoridade
GitHub NÃO é autoridade normativa para definir tag ISA, simbologia obrigatória, filosofia de controle ou requisito legal.

Hierarquia obrigatória:
1. documentos aprovados do projeto;
2. padrão AUTOMAÇÃO DM aplicável;
3. lista de instrumentos, I/O, C&E, lógica, datasheets e memoriais;
4. normas oficiais/licenciadas e legislação;
5. documentação oficial de fabricantes;
6. livros e artigos acadêmicos;
7. GitHub/open source.

Uma fonte GitHub pode suportar arquitetura de dados, parsing, DEXPI, grafos, validação e automação, mas nunca elevar sozinha um verbete a CONFIRMADO_NORMATIVO.

## Fluxo obrigatório por verbete
TERMO/TAG -> DISCIPLINA -> TIPO DE OBJETO -> DEFINIÇÃO -> FUNÇÃO -> SÍMBOLO -> RELACIONAMENTOS -> DOCUMENTOS -> FONTE -> EVIDÊNCIA -> STATUS -> QA/QC.

## Status permitidos
- CONFIRMADO_PROJETO
- CONFIRMADO_NORMATIVO
- SUPORTADO_GITHUB
- CONFIRMADO_COM_RESSALVA
- PROPOSTO
- CONFLITANTE
- TBD
- NÃO_APLICÁVEL

## Classes de evidência
- E1_PROJECT_DRAWING
- E2_PROJECT_DOCUMENT
- E3_FORMAL_CONFIRMATION
- E4_OFFICIAL_STANDARD
- E5_MANUFACTURER
- E6_ACADEMIC_BOOK_PAPER
- E7_GITHUB_OPEN_SOURCE
- E0_NO_EVIDENCE

## Regra contra invenção
Se não houver evidência suficiente, registrar exatamente:
`PENDENTE — NÃO HÁ EVIDÊNCIA SUFICIENTE PARA DEFINIR.`

Nunca inventar tag, símbolo, variável, intertravamento, set point, estado de falha, protocolo, grandeza elétrica ou relação funcional.

## Regras de atualização automática
1. O pipeline verifica repositórios GitHub autorizados em `datacenter/GLOSSARY_SOURCES.json`.
2. Mudanças upstream atualizam apenas metadados de fonte e a fila de candidatos.
3. Nenhuma mudança de conteúdo técnico é promovida automaticamente a CONFIRMADO_NORMATIVO.
4. O workflow executa validação em push/PR e sincronização programada.
5. O estado de execução deve ser verificável por GitHub Actions.

## Fontes GitHub iniciais permitidas
- DEXPI/Specification — modelo de dados/intercâmbio P&ID.
- process-intelligence-research/pyDEXPI — implementação Python, parsing/modelagem/grafos.

## Estrutura mínima de cada verbete
- id
- term
- aliases
- discipline
- object_type
- definition_pt
- definition_en
- function
- symbol_family
- tag_pattern
- relationships
- related_documents
- source_refs
- evidence_class
- status
- project_specific
- normative_warning
- last_reviewed_at

## QA/QC bloqueante
Bloquear publicação se ocorrer qualquer um dos casos:
- verbete sem fonte;
- fonte GitHub tratada como norma;
- status confirmado sem classe de evidência compatível;
- tag sem disciplina/tipo de objeto;
- símbolo sem família/localização quando aplicável;
- relação órfã;
- duplicidade de ID;
- conteúdo técnico alterado automaticamente sem revisão.

## Saída esperada
O sistema deve produzir:
1. glossário mestre JSON validado;
2. datasheet padrão de verbete;
3. estado das fontes GitHub;
4. fila de candidatos quando upstream mudar;
5. relatório de validação;
6. execução rastreável no GitHub Actions.
