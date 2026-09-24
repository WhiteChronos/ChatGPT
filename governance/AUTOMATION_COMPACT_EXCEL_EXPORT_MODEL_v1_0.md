# Automation Compact Excel Export Model v1.0

## Status
GOLDEN RULE / EXTERNAL-REVIEW EXPORT PROFILE

## Purpose
Define the default compact XLSX presentation for Automation compatibility reviews when the workbook is intended for human circulation/review.

This profile changes presentation only. It SHALL NOT remove evidence, decisions, findings, Protocol Zero history or release blockers from the underlying compatibility dataset.

## Default workbook layout
Use four sheets by default:

1. `00_Resumo`
   - executive situation;
   - key counts;
   - closed decisions;
   - Release Gate and closure conditions.

2. `01_Documentos_e_Acoes`
   - one consolidated row per document/revision;
   - priority;
   - objective action required to resolve the document;
   - related finding/pending IDs;
   - status.
   - Do not duplicate a full finding register when document-oriented action is enough for the reviewer.

3. `02_Pendencias`
   - ID;
   - priority;
   - theme/class;
   - pending condition;
   - next objective action;
   - expected document/deliverable;
   - status.

4. `03_Perguntas_Respondidas`
   - question ID;
   - theme;
   - original question;
   - user's answer;
   - consolidated treatment/decision;
   - status;
   - evidence/project documents;
   - traceability note.

## Default exclusions
Do not create separate sheets for the following unless explicitly requested:
- standalone evidence register;
- standalone decisions register;
- standalone findings register;
- standalone Release Gate;
- external-evaluation form;
- responsible/owner matrix.

Evidence remains visible in the relevant document/action, pending or question rows.

## Consolidation rules
- Decisions and Release Gate belong in the Summary sheet.
- Findings are consolidated into the Documents & Actions sheet by the document that must be corrected.
- A document row SHALL state what must be done to solve the problem, not merely restate the finding.
- Use the highest applicable priority for the document row.
- Related finding/pending IDs preserve traceability without multiplying rows.
- Keep the Pending sheet separate and organized by priority and next action.
- Keep answered questions separate because they preserve Protocol Zero audit history, including superseded answers.
- Never delete a superseded user answer; mark it as superseded and point to the final decision.

## Design rules
- prefer compact, readable tables over many tabs;
- wrap long text;
- freeze headers;
- hide gridlines;
- use A4 print setup;
- use thicker external borders and normal internal separators;
- do not use an owner/responsible column by default;
- do not include external-review input fields unless the user explicitly requests an evaluation form.

## Relation to /visualize
The interactive /visualize report remains comprehensive. The compact XLSX is a reviewer-oriented projection of the same governed data, not a replacement for the full technical model.
