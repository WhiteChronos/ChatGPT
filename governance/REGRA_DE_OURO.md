# REGRA DE OURO — AUTOMAÇÃO DM R00-05

## 1. Simbologia

Nunca sair do padrão de simbologia AUTOMAÇÃO DM R00-05 aprovado para o projeto.

Famílias permitidas:
- Instrumento discreto: círculo.
- Display compartilhado: círculo inscrito em quadrado.
- Função executada em computador: hexágono.
- Função executada em PLC: losango inscrito em quadrado.

## 2. Dimensão nominal

Todos os símbolos funcionais devem possuir dimensão externa nominal de 12 mm.

- círculo: Ø 12 mm;
- círculo em quadrado: quadrado externo 12 x 12 mm;
- hexágono: envoltória externa nominal de 12 mm;
- losango em quadrado: quadrado externo 12 x 12 mm.

É proibido achatar, alongar, comprimir ou ampliar símbolos para acomodar texto ou layout.

O texto se adapta ao símbolo. O símbolo nunca se adapta ao texto.

## 3. Localização

A localização deve ser representada conforme o padrão do projeto:
- campo: sem linha horizontal;
- painel principal: uma linha contínua;
- atrás do painel: uma linha tracejada;
- painel local/equipamento: duas linhas contínuas.

## 4. Classificação antes do desenho

A ordem obrigatória é:

FUNÇÃO -> PLATAFORMA DE EXECUÇÃO -> LOCALIZAÇÃO -> SÍMBOLO AUTOMAÇÃO DM -> 12 mm -> LAYOUT.

Nunca escolher geometria por estética ou por espaço disponível.

## 5. Lógica funcional

- CMD != RUN.
- RUN != FAULT.
- AVAILABLE é estado independente.
- CMD, RUN, FAULT e AVAILABLE são papéis funcionais distintos e não estados genéricos de execução de software.
- MAN/AUTO != LOCAL/REMOTO.
- Alarme não implica trip.
- Intertravamento exige causa, condição, efeito, equipamento afetado, feedback, reset, estado seguro e evidência.
- Sinal sem origem, destino, tipo, direção e função é órfão e bloqueante.

## 6. Informação documental

Nenhuma função, temporização, estado seguro, fail position, intertravamento, setpoint, sequência ou comunicação pode ser inventada.

Status aceitos:
- CONFIRMADO
- CONFIRMADO_COM_RESSALVA
- PROPOSTO
- CONFLITANTE
- TBD
- NÃO_APLICÁVEL

## 7. Regra de emissão

Qualquer violação deste documento é NÃO CONFORMIDADE CRÍTICA e bloqueia a aprovação da representação até correção ou justificativa técnica aprovada e rastreável.

## 8. Governança de mudança

Arquivos de CI, agentes, prompts, schemas ou sugestões automáticas não podem simplificar, substituir ou redefinir estas regras de engenharia apenas para fazer o workflow passar. Toda alteração de conteúdo de domínio deve preservar rastreabilidade, motivo técnico, revisão e teste de regressão correspondente.

## 9. Compatibilização e referências
Toda compatibilização de Automação SHALL seguir o modelo `AUTOMATION_COMPATIBILITY_REPORT_MODEL_v1_0`, o Protocol Zero e a biblioteca `datacenter/AUTOMATION_REFERENCE_LIBRARY.json`.

Antes de perguntar uma dúvida técnica ao usuário, consultar a baseline do projeto e as fontes normativas/oficiais aplicáveis. Norma fora de escopo pode orientar boa prática, mas não cria não conformidade sozinha.

Todo erro confirmado deve mostrar os documentos envolvidos: evidência, correlatos/conflitantes, normas/referências e documentos a corrigir.

## 10. Formato obrigatório de perguntas
Em compatibilização de Automação, perguntas ao usuário também fazem parte do relatório técnico e devem permanecer no padrão visual aprovado.

É proibido substituir o módulo visual de perguntas por uma lista simples em Markdown quando houver superfície interativa disponível.

Cada pergunta deve mostrar: ID, criticidade/prioridade, área, pergunta objetiva, motivo, documentos do projeto envolvidos, fontes já verificadas, status e campo de resposta. Após resposta, a pergunta migra para “Perguntas Resolvidas” e o Protocol Zero é reexecutado antes de qualquer promoção para erro/finding.

## 11. Regra de evidência antes de associação
Não presumir relação elétrica, funcional ou quantitativa entre itens sem evidência do projeto.

É proibido concluir, por exemplo, que quantidade de DO = quantidade de relés, ou que um TAG RI está ligado a um DO específico, apenas por nome, contagem ou proximidade em lista.

Antes da afirmação técnica:
1. verificar documento do projeto;
2. verificar base/contrato;
3. verificar norma aplicável;
4. verificar fabricante oficial;
5. buscar livro/artigo técnico de apoio;
6. pesquisar GitHub/repositórios open source e plugins de pesquisa quando ajudarem a entender o conceito;
7. somente então formular hipótese/pergunta.

GitHub, repositórios open source e plugins são apoio de pesquisa, nunca substituem evidência do projeto, norma aplicável ou fabricante oficial.

Aplicar `governance/AUTOMATION_EVIDENCE_RESEARCH_GOLDEN_RULE_v1_0.md` e `datacenter/AUTOMATION_TECHNICAL_KNOWLEDGE_BASE.json`.

## 12. Exportação Excel compacta
Para relatórios de compatibilização de Automação enviados em XLSX para circulação/revisão, aplicar `AUTOMATION_COMPACT_XLSX_V1`.

Padrão:
- Resumo contém decisões e Release Gate;
- Findings são consolidados por documento em “Documentos e Ações”, mostrando objetivamente o que corrigir e a prioridade;
- Pendências permanecem em uma aba organizada;
- Perguntas respondidas permanecem em aba própria para rastreabilidade do Protocol Zero;
- não criar abas separadas de Evidências, Decisões, Findings, Release Gate, Avaliação Externa ou Responsáveis salvo pedido explícito.

A compactação é somente de apresentação e não pode apagar evidência ou rastreabilidade técnica.
