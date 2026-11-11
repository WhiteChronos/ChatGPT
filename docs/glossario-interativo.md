# Glossário técnico interativo

<div class="deks-glossary-hero">
  <p class="deks-eyebrow">DEKS · Digital Engineering Knowledge System</p>
  <h2>Glossário Rev4.2 → AUTOMAÇÃO DM → tags/símbolos → P&amp;ID → Instrument Index/I/O → C&amp;E → datasheets</h2>
  <p>Consulta unificada com separação rígida entre <strong>base aprovada</strong> e <strong>staging técnico</strong>. Registros em staging nunca são apresentados como conhecimento aprovado.</p>
</div>

<div class="deks-metrics">
  <div class="deks-metric"><strong>2</strong><span>verbetes na base aprovada</span></div>
  <div class="deks-metric"><strong>40</strong><span>registros em staging</span></div>
  <div class="deks-metric"><strong>40</strong><span>REVIEW_REQUIRED</span></div>
  <div class="deks-metric"><strong>16</strong><span>símbolos AUTOMAÇÃO DM</span></div>
  <div class="deks-metric"><strong>4</strong><span>fontes bloqueadas por falta de arquivo</span></div>
</div>

<div class="deks-governance-callout">
  <strong>Regra de governança:</strong> INGESTÃO NÃO É APROVAÇÃO. O gerador lê <code>GLOSSARY_MASTER.json</code> em modo somente leitura e exibe staging separado.
</div>

<div class="deks-scope-tabs" role="group" aria-label="Escopo do glossário">
  <button type="button" class="deks-scope-button is-active" data-glossary-scope="all">Tudo</button>
  <button type="button" class="deks-scope-button" data-glossary-scope="canonical">Base aprovada</button>
  <button type="button" class="deks-scope-button" data-glossary-scope="staging">Staging</button>
  <button type="button" class="deks-scope-button" data-glossary-scope="symbol">Símbolos DM</button>
</div>

<div class="deks-controls deks-glossary-controls">
  <input id="deks-glossary-search" type="search" placeholder="Pesquisar termo, tag, função, símbolo, fonte ou documento" aria-label="Pesquisar no glossário">
  <select id="deks-glossary-source" aria-label="Filtrar por fonte"><option value="">Todas as fontes</option><option value="AUTOMACAO_DM_R00_05">AUTOMACAO_DM_R00_05</option><option value="GH-DEXPI-SPEC">GH-DEXPI-SPEC</option><option value="PROJECT_GLOSSARY_REV4_2">PROJECT_GLOSSARY_REV4_2</option><option value="PROJECT_PID">PROJECT_PID</option></select>
  <select id="deks-glossary-entity" aria-label="Filtrar por tipo"><option value="">Todos os tipos</option><option value="data_model">data_model</option><option value="glossary_entry">glossary_entry</option><option value="instrument">instrument</option><option value="pid_object">pid_object</option><option value="source">source</option><option value="symbol">symbol</option><option value="tag">tag</option></select>
  <select id="deks-glossary-status" aria-label="Filtrar por status"><option value="">Todos os status</option><option value="CONFIRMADO_PROJETO">CONFIRMADO_PROJETO</option><option value="REVIEW_REQUIRED">REVIEW_REQUIRED</option><option value="SUPORTADO_GITHUB">SUPORTADO_GITHUB</option></select>
  <select id="deks-glossary-evidence" aria-label="Filtrar por evidência"><option value="">Todas as classes de evidência</option><option value="E1_PROJECT_DRAWING">E1_PROJECT_DRAWING</option><option value="E2_PROJECT_DOCUMENT">E2_PROJECT_DOCUMENT</option><option value="E7_GITHUB_OPEN_SOURCE">E7_GITHUB_OPEN_SOURCE</option></select>
  <select id="deks-glossary-sort" aria-label="Ordenar resultados">
    <option value="title">Ordenar por termo / ID</option>
    <option value="source">Ordenar por fonte</option>
    <option value="entity">Ordenar por tipo</option>
    <option value="status">Ordenar por status</option>
  </select>
</div>

<div class="deks-result-row">
  <div id="deks-glossary-result-count" class="deks-result-count"></div>
  <button id="deks-glossary-reset" type="button" class="deks-reset-button">Limpar filtros</button>
</div>

<div id="deks-glossary-grid" class="deks-glossary-grid">
<article class="deks-glossary-card" data-scope="canonical" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="instrument" data-status="CONFIRMADO_PROJETO" data-evidence="E2_PROJECT_DOCUMENT" data-title="pt" data-search="pt pressure transmitter instrumentation, automation instrument transmissor de pressão. mede pressão e transmite o valor ao sistema conforme a arquitetura do projeto. project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-approved">BASE APROVADA</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>
  <h3>PT</h3>
  <p>Transmissor de pressão.</p>
  <div class="deks-card-meta">instrumentation, automation · instrument · CONFIRMADO_PROJETO</div>
  <button class="deks-open-entry" type="button">Abrir ficha técnica</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-approved">BASE APROVADA — leitura do datacenter canônico</div>
    <h2>PT</h2>
    <table class="deks-detail-table"><tr><th>ID</th><td><pre>TAG-PT</pre></td></tr><tr><th>Termo / Tag</th><td><pre>PT</pre></td></tr><tr><th>Aliases</th><td><pre>[
  &quot;Pressure Transmitter&quot;
]</pre></td></tr><tr><th>Disciplina</th><td><pre>[
  &quot;instrumentation&quot;,
  &quot;automation&quot;
]</pre></td></tr><tr><th>Tipo de objeto</th><td><pre>instrument</pre></td></tr><tr><th>Definição</th><td><pre>Transmissor de pressão.</pre></td></tr><tr><th>Função</th><td><pre>Mede pressão e transmite o valor ao sistema conforme a arquitetura do projeto.</pre></td></tr><tr><th>Padrão de tag</th><td><pre>PT-&lt;loop&gt;</pre></td></tr><tr><th>Família de símbolo</th><td><pre>project_or_standard_defined</pre></td></tr><tr><th>Localização</th><td><pre>project_defined</pre></td></tr><tr><th>Relações</th><td><pre>[
  &quot;PI&quot;,
  &quot;PIC&quot;,
  &quot;PSH&quot;,
  &quot;PDT&quot;,
  &quot;PV&quot;
]</pre></td></tr><tr><th>Documentos relacionados</th><td><pre>[
  &quot;P&amp;ID&quot;,
  &quot;Instrument Index&quot;,
  &quot;I/O List&quot;,
  &quot;Loop Diagram&quot;,
  &quot;Datasheet&quot;
]</pre></td></tr><tr><th>Fontes</th><td><pre>[
  &quot;PROJECT_GLOSSARY_REV4_2&quot;
]</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Status</th><td><pre>CONFIRMADO_PROJETO</pre></td></tr><tr><th>Última revisão</th><td><pre>2026-08-28</pre></td></tr><tr><th>Ressalva</th><td><pre>Validar identificação final pela legenda e critério do projeto.</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card" data-scope="canonical" data-source="GH-DEXPI-SPEC" data-entity="data_model" data-status="SUPORTADO_GITHUB" data-evidence="E7_GITHUB_OPEN_SOURCE" data-title="dexpi" data-search="dexpi data exchange in the process industry process, instrumentation, digital_engineering data_model referência de modelo e intercâmbio de dados para informação de engenharia de processo/p&amp;id. apoiar representação estruturada e intercâmbio de objetos do p&amp;id. gh-dexpi-spec">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-approved">BASE APROVADA</span><span class="deks-badge">E7_GITHUB_OPEN_SOURCE</span></div>
  <h3>DEXPI</h3>
  <p>Referência de modelo e intercâmbio de dados para informação de engenharia de processo/P&amp;ID.</p>
  <div class="deks-card-meta">process, instrumentation, digital_engineering · data_model · SUPORTADO_GITHUB</div>
  <button class="deks-open-entry" type="button">Abrir ficha técnica</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-approved">BASE APROVADA — leitura do datacenter canônico</div>
    <h2>DEXPI</h2>
    <table class="deks-detail-table"><tr><th>ID</th><td><pre>MODEL-DEXPI</pre></td></tr><tr><th>Termo / Tag</th><td><pre>DEXPI</pre></td></tr><tr><th>Aliases</th><td><pre>[
  &quot;Data Exchange in the Process Industry&quot;
]</pre></td></tr><tr><th>Disciplina</th><td><pre>[
  &quot;process&quot;,
  &quot;instrumentation&quot;,
  &quot;digital_engineering&quot;
]</pre></td></tr><tr><th>Tipo de objeto</th><td><pre>data_model</pre></td></tr><tr><th>Definição</th><td><pre>Referência de modelo e intercâmbio de dados para informação de engenharia de processo/P&amp;ID.</pre></td></tr><tr><th>Função</th><td><pre>Apoiar representação estruturada e intercâmbio de objetos do P&amp;ID.</pre></td></tr><tr><th>Padrão de tag</th><td><pre>not_applicable</pre></td></tr><tr><th>Família de símbolo</th><td><pre>not_applicable</pre></td></tr><tr><th>Localização</th><td><pre>not_applicable</pre></td></tr><tr><th>Relações</th><td><pre>[
  &quot;P&amp;ID inteligente&quot;,
  &quot;IEC 62424&quot;,
  &quot;pyDEXPI&quot;
]</pre></td></tr><tr><th>Documentos relacionados</th><td><pre>[
  &quot;Data Model&quot;,
  &quot;P&amp;ID&quot;,
  &quot;Engineering Database&quot;
]</pre></td></tr><tr><th>Fontes</th><td><pre>[
  &quot;GH-DEXPI-SPEC&quot;
]</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E7_GITHUB_OPEN_SOURCE</pre></td></tr><tr><th>Status</th><td><pre>SUPORTADO_GITHUB</pre></td></tr><tr><th>Última revisão</th><td><pre>2026-08-28</pre></td></tr><tr><th>Ressalva</th><td><pre>Fonte GitHub usada como referência de modelo/software; não substitui norma oficial nem critério do projeto.</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="source" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="glossario-rev4.2" data-search="glossario-rev4.2 source project_glossary_rev4_2 e2_project_document review_required document_title: glossário mestre multidisciplinar de fluxogramas de engenharia; edition: 4.2; edition_date: 2026-07; normative_base_date: 2026-07-22; scope: process, piping, instrumentation, automation, electrical, functional_safety, hvac, mechanical, hydraulic, pneumatic, fire_gas, telecom_ot, software, interlocks, control_strategies, tags_functions; governance: project_legend_and_approved_documents_precede_generic_interpretation: true; conflict_hierarchy: law_regulation, contract_client, corporate_standard, national_international_standard, project_criteria_specification, drawing_legend_notes, engineering_practice document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 2; section: controle e finalidade do documento; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>GLOSSARIO-REV4.2</h3>
  <p>Glossário Mestre Multidisciplinar de Fluxogramas de Engenharia</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · source · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>GLOSSARIO-REV4.2</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-9d8db1c687d9051381b0</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>source</pre></td></tr><tr><th>External ID</th><td><pre>GLOSSARIO-REV4.2</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;document_title&quot;: &quot;Glossário Mestre Multidisciplinar de Fluxogramas de Engenharia&quot;,
  &quot;edition&quot;: &quot;4.2&quot;,
  &quot;edition_date&quot;: &quot;2026-07&quot;,
  &quot;governance&quot;: {
    &quot;conflict_hierarchy&quot;: [
      &quot;law_regulation&quot;,
      &quot;contract_client&quot;,
      &quot;corporate_standard&quot;,
      &quot;national_international_standard&quot;,
      &quot;project_criteria_specification&quot;,
      &quot;drawing_legend_notes&quot;,
      &quot;engineering_practice&quot;
    ],
    &quot;project_legend_and_approved_documents_precede_generic_interpretation&quot;: true
  },
  &quot;normative_base_date&quot;: &quot;2026-07-22&quot;,
  &quot;scope&quot;: [
    &quot;process&quot;,
    &quot;piping&quot;,
    &quot;instrumentation&quot;,
    &quot;automation&quot;,
    &quot;electrical&quot;,
    &quot;functional_safety&quot;,
    &quot;hvac&quot;,
    &quot;mechanical&quot;,
    &quot;hydraulic&quot;,
    &quot;pneumatic&quot;,
    &quot;fire_gas&quot;,
    &quot;telecom_ot&quot;,
    &quot;software&quot;,
    &quot;interlocks&quot;,
    &quot;control_strategies&quot;,
    &quot;tags_functions&quot;
  ]
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 2,
  &quot;section&quot;: &quot;Controle e finalidade do documento&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="glossary_entry" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="p&amp;id" data-search="p&amp;id glossary_entry project_glossary_rev4_2 e2_project_document review_required term: p&amp;id; en: piping and instrumentation diagram; definition_pt: documento detalhado de equipamentos, tubulações, válvulas, acessórios, instrumentos e funções de controle.; application: base multidisciplinar de projeto, hazop, operação e manutenção. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 10; section: tipos de fluxogramas e documentos de engenharia; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>P&amp;ID</h3>
  <p>Documento detalhado de equipamentos, tubulações, válvulas, acessórios, instrumentos e funções de controle.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · glossary_entry · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>P&amp;ID</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-bf45652c623c7913925a</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>glossary_entry</pre></td></tr><tr><th>External ID</th><td><pre>P&amp;ID</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;application&quot;: &quot;Base multidisciplinar de projeto, HAZOP, operação e manutenção.&quot;,
  &quot;definition_pt&quot;: &quot;Documento detalhado de equipamentos, tubulações, válvulas, acessórios, instrumentos e funções de controle.&quot;,
  &quot;en&quot;: &quot;Piping and Instrumentation Diagram&quot;,
  &quot;term&quot;: &quot;P&amp;ID&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 10,
  &quot;section&quot;: &quot;Tipos de fluxogramas e documentos de engenharia&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="glossary_entry" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="p&amp;id_inteligente" data-search="p&amp;id_inteligente glossary_entry project_glossary_rev4_2 e2_project_document review_required term: p&amp;id inteligente; en: data-centric p&amp;id; definition_pt: p&amp;id associado a objetos e atributos de banco de dados para validação e troca de informações entre ferramentas.; application: engenharia digital e integração pce-cae. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 10; section: tipos de fluxogramas e documentos de engenharia; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>P&amp;ID_INTELIGENTE</h3>
  <p>P&amp;ID associado a objetos e atributos de banco de dados para validação e troca de informações entre ferramentas.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · glossary_entry · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>P&amp;ID_INTELIGENTE</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-bf2b65466afae0c7f67b</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>glossary_entry</pre></td></tr><tr><th>External ID</th><td><pre>P&amp;ID_INTELIGENTE</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;application&quot;: &quot;Engenharia digital e integração PCE-CAE.&quot;,
  &quot;definition_pt&quot;: &quot;P&amp;ID associado a objetos e atributos de banco de dados para validação e troca de informações entre ferramentas.&quot;,
  &quot;en&quot;: &quot;Data-centric P&amp;ID&quot;,
  &quot;term&quot;: &quot;P&amp;ID inteligente&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 10,
  &quot;section&quot;: &quot;Tipos de fluxogramas e documentos de engenharia&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="glossary_entry" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="simbolo_grafico" data-search="simbolo_grafico glossary_entry project_glossary_rev4_2 e2_project_document review_required term: símbolo gráfico; definition_pt: representação visual normalizada ou definida pela legenda para objeto, equipamento, instrumento ou função.; governance: a legenda do desenho específico deve ser consultada antes de atribuir significado definitivo. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 13; section: elementos gráficos, linhas, fronteiras e leitura; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>SIMBOLO_GRAFICO</h3>
  <p>Representação visual normalizada ou definida pela legenda para objeto, equipamento, instrumento ou função.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · glossary_entry · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>SIMBOLO_GRAFICO</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-96d7f9aa1cea4087b660</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>glossary_entry</pre></td></tr><tr><th>External ID</th><td><pre>SIMBOLO_GRAFICO</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;definition_pt&quot;: &quot;Representação visual normalizada ou definida pela legenda para objeto, equipamento, instrumento ou função.&quot;,
  &quot;governance&quot;: &quot;A legenda do desenho específico deve ser consultada antes de atribuir significado definitivo.&quot;,
  &quot;term&quot;: &quot;Símbolo gráfico&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 13,
  &quot;section&quot;: &quot;Elementos gráficos, linhas, fronteiras e leitura&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="glossary_entry" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="legenda" data-search="legenda glossary_entry project_glossary_rev4_2 e2_project_document review_required term: legenda; definition_pt: conjunto de convenções gráficas e significados aplicáveis ao documento.; governance: primeira referência para interpretar símbolos e linhas do desenho específico. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 13; section: elementos gráficos, linhas, fronteiras e leitura; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>LEGENDA</h3>
  <p>Conjunto de convenções gráficas e significados aplicáveis ao documento.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · glossary_entry · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>LEGENDA</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-28629a28af5925f5f7ee</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>glossary_entry</pre></td></tr><tr><th>External ID</th><td><pre>LEGENDA</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;definition_pt&quot;: &quot;Conjunto de convenções gráficas e significados aplicáveis ao documento.&quot;,
  &quot;governance&quot;: &quot;Primeira referência para interpretar símbolos e linhas do desenho específico.&quot;,
  &quot;term&quot;: &quot;Legenda&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 13,
  &quot;section&quot;: &quot;Elementos gráficos, linhas, fronteiras e leitura&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="glossary_entry" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="tag" data-search="tag glossary_entry project_glossary_rev4_2 e2_project_document review_required term: tag; definition_pt: código controlado que identifica objeto, função, equipamento ou documento.; caution: não confundir tag funcional isa com reference designation iec 81346. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 13; section: elementos gráficos, linhas, fronteiras e leitura; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>TAG</h3>
  <p>Código controlado que identifica objeto, função, equipamento ou documento.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · glossary_entry · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>TAG</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-3668d719f786e1137be0</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>glossary_entry</pre></td></tr><tr><th>External ID</th><td><pre>TAG</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;caution&quot;: &quot;Não confundir tag funcional ISA com reference designation IEC 81346.&quot;,
  &quot;definition_pt&quot;: &quot;Código controlado que identifica objeto, função, equipamento ou documento.&quot;,
  &quot;term&quot;: &quot;Tag&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 13,
  &quot;section&quot;: &quot;Elementos gráficos, linhas, fronteiras e leitura&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="glossary_entry" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="instrument_index" data-search="instrument_index glossary_entry project_glossary_rev4_2 e2_project_document review_required term: lista de instrumentos; en: instrument index; definition_pt: cadastro mestre de tags, serviços, tipos, documentos e dados de instrumentos.; consistency: deve permanecer coerente com p&amp;id e i/o. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 33; section: documentos de engenharia; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>INSTRUMENT_INDEX</h3>
  <p>Cadastro mestre de tags, serviços, tipos, documentos e dados de instrumentos.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · glossary_entry · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>INSTRUMENT_INDEX</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-dc3eeec222b229ace100</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>glossary_entry</pre></td></tr><tr><th>External ID</th><td><pre>INSTRUMENT_INDEX</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;consistency&quot;: &quot;Deve permanecer coerente com P&amp;ID e I/O.&quot;,
  &quot;definition_pt&quot;: &quot;Cadastro mestre de tags, serviços, tipos, documentos e dados de instrumentos.&quot;,
  &quot;en&quot;: &quot;Instrument index&quot;,
  &quot;term&quot;: &quot;Lista de instrumentos&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 33,
  &quot;section&quot;: &quot;Documentos de engenharia&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="glossary_entry" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="io_list" data-search="io_list glossary_entry project_glossary_rev4_2 e2_project_document review_required term: lista de i/o; en: i/o list; definition_pt: cadastro de entradas e saídas dos sistemas de controle relacionando tag, canal, tipo de sinal e sistema.; consistency: p&amp;id x i/o deve confirmar canais, tipos, sistemas e interfaces dos objetos com sinais. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 34; section: matriz de consistência entre documentos; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>IO_LIST</h3>
  <p>Cadastro de entradas e saídas dos sistemas de controle relacionando tag, canal, tipo de sinal e sistema.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · glossary_entry · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>IO_LIST</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-fe43f1fedeb995400a9e</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>glossary_entry</pre></td></tr><tr><th>External ID</th><td><pre>IO_LIST</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;consistency&quot;: &quot;P&amp;ID x I/O deve confirmar canais, tipos, sistemas e interfaces dos objetos com sinais.&quot;,
  &quot;definition_pt&quot;: &quot;Cadastro de entradas e saídas dos sistemas de controle relacionando tag, canal, tipo de sinal e sistema.&quot;,
  &quot;en&quot;: &quot;I/O list&quot;,
  &quot;term&quot;: &quot;Lista de I/O&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 34,
  &quot;section&quot;: &quot;Matriz de consistência entre documentos&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="glossary_entry" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="cause_effect" data-search="cause_effect glossary_entry project_glossary_rev4_2 e2_project_document review_required term: matriz de causa e efeito; en: cause &amp; effect; definition_pt: matriz que relaciona causas iniciadoras a efeitos automáticos, alarmes, paradas e outras ações.; consistency: p&amp;id x c&amp;e deve manter causas, setpoints, efeitos, prioridades e estados seguros coerentes. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 11; section: tipos de fluxogramas e documentos de engenharia; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>CAUSE_EFFECT</h3>
  <p>Matriz que relaciona causas iniciadoras a efeitos automáticos, alarmes, paradas e outras ações.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · glossary_entry · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>CAUSE_EFFECT</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-7140c42d024c0b5bd853</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>glossary_entry</pre></td></tr><tr><th>External ID</th><td><pre>CAUSE_EFFECT</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;consistency&quot;: &quot;P&amp;ID x C&amp;E deve manter causas, setpoints, efeitos, prioridades e estados seguros coerentes.&quot;,
  &quot;definition_pt&quot;: &quot;Matriz que relaciona causas iniciadoras a efeitos automáticos, alarmes, paradas e outras ações.&quot;,
  &quot;en&quot;: &quot;Cause &amp; Effect&quot;,
  &quot;term&quot;: &quot;Matriz de causa e efeito&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 11,
  &quot;section&quot;: &quot;Tipos de fluxogramas e documentos de engenharia&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="glossary_entry" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="datasheet" data-search="datasheet glossary_entry project_glossary_rev4_2 e2_project_document review_required term: data sheet; pt: folha de dados; definition_pt: documento estruturado com requisitos e características de um item.; application: compra, fabricação e validação. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 33; section: documentos de engenharia; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>DATASHEET</h3>
  <p>Documento estruturado com requisitos e características de um item.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · glossary_entry · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>DATASHEET</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-4fa844eb4609a239704a</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>glossary_entry</pre></td></tr><tr><th>External ID</th><td><pre>DATASHEET</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;application&quot;: &quot;Compra, fabricação e validação.&quot;,
  &quot;definition_pt&quot;: &quot;Documento estruturado com requisitos e características de um item.&quot;,
  &quot;pt&quot;: &quot;Folha de dados&quot;,
  &quot;term&quot;: &quot;Data sheet&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 33,
  &quot;section&quot;: &quot;Documentos de engenharia&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="tag" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="tag_caution_tc" data-search="tag_caution_tc tag project_glossary_rev4_2 e2_project_document review_required code: tc; interpretation_pt: controlador de temperatura; caution: não usar tc para deduzir tecnologia de termopar. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 35; section: nota técnica sobre tc, kqr, xy, uy e clp; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>TAG_CAUTION_TC</h3>
  <p>Registro técnico em staging: TAG_CAUTION_TC.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · tag · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>TAG_CAUTION_TC</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-6b98c70bb4276b78f4d9</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>tag</pre></td></tr><tr><th>External ID</th><td><pre>TAG_CAUTION_TC</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;caution&quot;: &quot;Não usar TC para deduzir tecnologia de termopar.&quot;,
  &quot;code&quot;: &quot;TC&quot;,
  &quot;interpretation_pt&quot;: &quot;Controlador de temperatura&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 35,
  &quot;section&quot;: &quot;Nota técnica sobre TC, KQR, XY, UY e CLP&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="tag" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="tag_caution_kqr" data-search="tag_caution_kqr tag project_glossary_rev4_2 e2_project_document review_required code: kqr; interpretation_pt: combinação pouco usual dependente da legenda; caution: não classificar como telerruptor sem definição formal do projeto. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 35; section: nota técnica sobre tc, kqr, xy, uy e clp; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>TAG_CAUTION_KQR</h3>
  <p>Registro técnico em staging: TAG_CAUTION_KQR.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · tag · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>TAG_CAUTION_KQR</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-d5fa867b48d44031440c</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>tag</pre></td></tr><tr><th>External ID</th><td><pre>TAG_CAUTION_KQR</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;caution&quot;: &quot;Não classificar como telerruptor sem definição formal do projeto.&quot;,
  &quot;code&quot;: &quot;KQR&quot;,
  &quot;interpretation_pt&quot;: &quot;Combinação pouco usual dependente da legenda&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 35,
  &quot;section&quot;: &quot;Nota técnica sobre TC, KQR, XY, UY e CLP&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="tag" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="tag_caution_xy" data-search="tag_caution_xy tag project_glossary_rev4_2 e2_project_document review_required code: xy; interpretation_pt: função auxiliar não classificada ou definida pelo usuário; caution: a legenda deve indicar hardware ou função. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 35; section: nota técnica sobre tc, kqr, xy, uy e clp; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>TAG_CAUTION_XY</h3>
  <p>Registro técnico em staging: TAG_CAUTION_XY.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · tag · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>TAG_CAUTION_XY</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-37f6d1d42213ad93d985</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>tag</pre></td></tr><tr><th>External ID</th><td><pre>TAG_CAUTION_XY</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;caution&quot;: &quot;A legenda deve indicar hardware ou função.&quot;,
  &quot;code&quot;: &quot;XY&quot;,
  &quot;interpretation_pt&quot;: &quot;Função auxiliar não classificada ou definida pelo usuário&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 35,
  &quot;section&quot;: &quot;Nota técnica sobre TC, KQR, XY, UY e CLP&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="tag" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="tag_caution_uy" data-search="tag_caution_uy tag project_glossary_rev4_2 e2_project_document review_required code: uy; interpretation_pt: função auxiliar/multifuncional associada a variável multivariável; caution: não é tag universal para o clp físico. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 35; section: nota técnica sobre tc, kqr, xy, uy e clp; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>TAG_CAUTION_UY</h3>
  <p>Registro técnico em staging: TAG_CAUTION_UY.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · tag · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>TAG_CAUTION_UY</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-353a0e95e91369b544c9</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>tag</pre></td></tr><tr><th>External ID</th><td><pre>TAG_CAUTION_UY</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;caution&quot;: &quot;Não é tag universal para o CLP físico.&quot;,
  &quot;code&quot;: &quot;UY&quot;,
  &quot;interpretation_pt&quot;: &quot;Função auxiliar/multifuncional associada a variável multivariável&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 35,
  &quot;section&quot;: &quot;Nota técnica sobre TC, KQR, XY, UY e CLP&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="tag" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="tag_caution_clp001" data-search="tag_caution_clp001 tag project_glossary_rev4_2 e2_project_document review_required code: clp-001; interpretation_pt: identificação de equipamento/sistema por acrônimo; caution: funções internas podem ter tags próprias; validade depende do critério do empreendimento. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 35; section: nota técnica sobre tc, kqr, xy, uy e clp; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>TAG_CAUTION_CLP001</h3>
  <p>Registro técnico em staging: TAG_CAUTION_CLP001.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · tag · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>TAG_CAUTION_CLP001</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-a7879b14802b8c7dab65</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>tag</pre></td></tr><tr><th>External ID</th><td><pre>TAG_CAUTION_CLP001</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;caution&quot;: &quot;Funções internas podem ter tags próprias; validade depende do critério do empreendimento.&quot;,
  &quot;code&quot;: &quot;CLP-001&quot;,
  &quot;interpretation_pt&quot;: &quot;Identificação de equipamento/sistema por acrônimo&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 35,
  &quot;section&quot;: &quot;Nota técnica sobre TC, KQR, XY, UY e CLP&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="tag" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="control_permissive" data-search="control_permissive tag project_glossary_rev4_2 e2_project_document review_required code: permissive; class: logic_function; meaning_pt: condição necessária para autorizar uma ação; requirement: distinguir permissivo de partida e de operação. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 151; section: glossário mestre de tags e funções; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>CONTROL_PERMISSIVE</h3>
  <p>Registro técnico em staging: CONTROL_PERMISSIVE.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · tag · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>CONTROL_PERMISSIVE</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-7f94b3b3dfe7d726352e</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>tag</pre></td></tr><tr><th>External ID</th><td><pre>CONTROL_PERMISSIVE</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;class&quot;: &quot;logic_function&quot;,
  &quot;code&quot;: &quot;PERMISSIVE&quot;,
  &quot;meaning_pt&quot;: &quot;Condição necessária para autorizar uma ação&quot;,
  &quot;requirement&quot;: &quot;Distinguir permissivo de partida e de operação.&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 151,
  &quot;section&quot;: &quot;Glossário Mestre de Tags e Funções&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="tag" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="control_trip" data-search="control_trip tag project_glossary_rev4_2 e2_project_document review_required code: trip; class: protection_function; meaning_pt: ação automática de parada ou bloqueio; requirement: definir first-out, reset e estado seguro. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 151; section: glossário mestre de tags e funções; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>CONTROL_TRIP</h3>
  <p>Registro técnico em staging: CONTROL_TRIP.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · tag · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>CONTROL_TRIP</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-3aa1c5cf268895feb2d8</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>tag</pre></td></tr><tr><th>External ID</th><td><pre>CONTROL_TRIP</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;class&quot;: &quot;protection_function&quot;,
  &quot;code&quot;: &quot;TRIP&quot;,
  &quot;meaning_pt&quot;: &quot;Ação automática de parada ou bloqueio&quot;,
  &quot;requirement&quot;: &quot;Definir first-out, reset e estado seguro.&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 151,
  &quot;section&quot;: &quot;Glossário Mestre de Tags e Funções&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="tag" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="control_bypass" data-search="control_bypass tag project_glossary_rev4_2 e2_project_document review_required code: bypass; class: temporary_function; meaning_pt: inibição controlada de canal ou função; requirement: requer autorização, alarme, registro e prazo. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 151; section: glossário mestre de tags e funções; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>CONTROL_BYPASS</h3>
  <p>Registro técnico em staging: CONTROL_BYPASS.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · tag · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>CONTROL_BYPASS</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-cdea6e53ab35f74f00cf</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>tag</pre></td></tr><tr><th>External ID</th><td><pre>CONTROL_BYPASS</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;class&quot;: &quot;temporary_function&quot;,
  &quot;code&quot;: &quot;BYPASS&quot;,
  &quot;meaning_pt&quot;: &quot;Inibição controlada de canal ou função&quot;,
  &quot;requirement&quot;: &quot;Requer autorização, alarme, registro e prazo.&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 151,
  &quot;section&quot;: &quot;Glossário Mestre de Tags e Funções&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="tag" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="control_reset" data-search="control_reset tag project_glossary_rev4_2 e2_project_document review_required code: reset; class: logic_function; meaning_pt: liberação de estado retentivo; requirement: somente após causa normalizada e permissivos atendidos. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 151; section: glossário mestre de tags e funções; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>CONTROL_RESET</h3>
  <p>Registro técnico em staging: CONTROL_RESET.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · tag · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>CONTROL_RESET</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-28d8ff2e8994c1afa81e</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>tag</pre></td></tr><tr><th>External ID</th><td><pre>CONTROL_RESET</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;class&quot;: &quot;logic_function&quot;,
  &quot;code&quot;: &quot;RESET&quot;,
  &quot;meaning_pt&quot;: &quot;Liberação de estado retentivo&quot;,
  &quot;requirement&quot;: &quot;Somente após causa normalizada e permissivos atendidos.&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 151,
  &quot;section&quot;: &quot;Glossário Mestre de Tags e Funções&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_GLOSSARY_REV4_2" data-entity="tag" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="control_first_out" data-search="control_first_out tag project_glossary_rev4_2 e2_project_document review_required code: first-out; class: diagnostic; meaning_pt: registro da primeira causa de trip; requirement: preservar causas individuais. document: glossario_mestre_instrumentacao_automacao_rev4_2.pdf; page: 151; section: glossário mestre de tags e funções; source_id: project_glossary_rev4_2">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>CONTROL_FIRST_OUT</h3>
  <p>Registro técnico em staging: CONTROL_FIRST_OUT.</p>

  <div class="deks-card-meta">PROJECT_GLOSSARY_REV4_2 · tag · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>CONTROL_FIRST_OUT</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-9282e8775de389eca22b</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9b569f7c07625955</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9b569f7c07625955.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_GLOSSARY_REV4_2</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>4.2</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>tag</pre></td></tr><tr><th>External ID</th><td><pre>CONTROL_FIRST_OUT</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;class&quot;: &quot;diagnostic&quot;,
  &quot;code&quot;: &quot;FIRST-OUT&quot;,
  &quot;meaning_pt&quot;: &quot;Registro da primeira causa de trip&quot;,
  &quot;requirement&quot;: &quot;Preservar causas individuais.&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;Glossario_Mestre_Instrumentacao_Automacao_Rev4_2.pdf&quot;,
  &quot;page&quot;: 151,
  &quot;section&quot;: &quot;Glossário Mestre de Tags e Funções&quot;,
  &quot;source_id&quot;: &quot;PROJECT_GLOSSARY_REV4_2&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_PID" data-entity="source" data-status="REVIEW_REQUIRED" data-evidence="E1_PROJECT_DRAWING" data-title="de-0244.00-8210-944-tp7-003" data-search="de-0244.00-8210-944-tp7-003 source project_pid e1_project_drawing review_required document_number: de-0244.00-8210-944-tp7-003; document_type: engineering_flow; project: reforma do prédio perimetral - cenpes; scope: fluxogramas típicos - casa de máquinas - fan coil; revision: d; pid_equivalence: not_assumed; note: ingestão limitada a metadados e objetos explicitamente identificados no documento disponível. document: de-0244.00-8210-944-tp7-003=d.pdf; page_range: 2-3; section: carimbo/título dos fluxogramas típicos; source_id: project_pid">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E1_PROJECT_DRAWING</span></div>

  <h3>DE-0244.00-8210-944-TP7-003</h3>
  <p>Registro técnico em staging: DE-0244.00-8210-944-TP7-003.</p>

  <div class="deks-card-meta">PROJECT_PID · source · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>DE-0244.00-8210-944-TP7-003</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-24556efd12e9cf2ed6bf</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9e6d8528ff88108b</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9e6d8528ff88108b.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_PID</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>D</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>source</pre></td></tr><tr><th>External ID</th><td><pre>DE-0244.00-8210-944-TP7-003</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E1_PROJECT_DRAWING</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;document_number&quot;: &quot;DE-0244.00-8210-944-TP7-003&quot;,
  &quot;document_type&quot;: &quot;engineering_flow&quot;,
  &quot;note&quot;: &quot;Ingestão limitada a metadados e objetos explicitamente identificados no documento disponível.&quot;,
  &quot;pid_equivalence&quot;: &quot;not_assumed&quot;,
  &quot;project&quot;: &quot;Reforma do Prédio Perimetral - CENPES&quot;,
  &quot;revision&quot;: &quot;D&quot;,
  &quot;scope&quot;: &quot;Fluxogramas típicos - casa de máquinas - fan coil&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;DE-0244.00-8210-944-TP7-003=D.pdf&quot;,
  &quot;page_range&quot;: &quot;2-3&quot;,
  &quot;section&quot;: &quot;Carimbo/título dos fluxogramas típicos&quot;,
  &quot;source_id&quot;: &quot;PROJECT_PID&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_PID" data-entity="pid_object" data-status="REVIEW_REQUIRED" data-evidence="E1_PROJECT_DRAWING" data-title="ac-0244.0002" data-search="ac-0244.0002 pid_object project_pid e1_project_drawing review_required tag: ac-0244.0002; object_class: fan_coil_system_reference; document_type: engineering_flow; drawing: de-0244.00-8210-944-tp7-003; sheet: 02 de 03; title_context: fluxogramas típicos - casa de máquinas - fancoil; status: confirmed_from_drawing_title; unverified_attributes: instrument_tags, io_channels, setpoints, cause_effect_rows, datasheet_values document: de-0244.00-8210-944-tp7-003=d.pdf; page: 2; section: título do desenho; source_id: project_pid">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E1_PROJECT_DRAWING</span></div>

  <h3>AC-0244.0002</h3>
  <p>AC-0244.0002</p>

  <div class="deks-card-meta">PROJECT_PID · pid_object · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>AC-0244.0002</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-a843b4651cbde1c5243b</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9e6d8528ff88108b</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9e6d8528ff88108b.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_PID</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>D</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>pid_object</pre></td></tr><tr><th>External ID</th><td><pre>AC-0244.0002</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E1_PROJECT_DRAWING</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;document_type&quot;: &quot;engineering_flow&quot;,
  &quot;drawing&quot;: &quot;DE-0244.00-8210-944-TP7-003&quot;,
  &quot;object_class&quot;: &quot;fan_coil_system_reference&quot;,
  &quot;sheet&quot;: &quot;02 de 03&quot;,
  &quot;status&quot;: &quot;CONFIRMED_FROM_DRAWING_TITLE&quot;,
  &quot;tag&quot;: &quot;AC-0244.0002&quot;,
  &quot;title_context&quot;: &quot;Fluxogramas típicos - casa de máquinas - fancoil&quot;,
  &quot;unverified_attributes&quot;: [
    &quot;instrument_tags&quot;,
    &quot;io_channels&quot;,
    &quot;setpoints&quot;,
    &quot;cause_effect_rows&quot;,
    &quot;datasheet_values&quot;
  ]
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;DE-0244.00-8210-944-TP7-003=D.pdf&quot;,
  &quot;page&quot;: 2,
  &quot;section&quot;: &quot;Título do desenho&quot;,
  &quot;source_id&quot;: &quot;PROJECT_PID&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="PROJECT_PID" data-entity="pid_object" data-status="REVIEW_REQUIRED" data-evidence="E1_PROJECT_DRAWING" data-title="ac-0244.0003" data-search="ac-0244.0003 pid_object project_pid e1_project_drawing review_required tag: ac-0244.0003; object_class: fan_coil_system_reference; document_type: engineering_flow; drawing: de-0244.00-8210-944-tp7-003; sheet: 03 de 03; title_context: fluxogramas típicos - casa de máquinas - fancoil; status: confirmed_from_drawing_title; unverified_attributes: instrument_tags, io_channels, setpoints, cause_effect_rows, datasheet_values document: de-0244.00-8210-944-tp7-003=d.pdf; page: 3; section: título do desenho; source_id: project_pid">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E1_PROJECT_DRAWING</span></div>

  <h3>AC-0244.0003</h3>
  <p>AC-0244.0003</p>

  <div class="deks-card-meta">PROJECT_PID · pid_object · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>AC-0244.0003</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-b04e6b80743c5d90443b</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-9e6d8528ff88108b</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-9e6d8528ff88108b.json</pre></td></tr><tr><th>Fonte</th><td><pre>PROJECT_PID</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>D</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>pid_object</pre></td></tr><tr><th>External ID</th><td><pre>AC-0244.0003</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E1_PROJECT_DRAWING</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;document_type&quot;: &quot;engineering_flow&quot;,
  &quot;drawing&quot;: &quot;DE-0244.00-8210-944-TP7-003&quot;,
  &quot;object_class&quot;: &quot;fan_coil_system_reference&quot;,
  &quot;sheet&quot;: &quot;03 de 03&quot;,
  &quot;status&quot;: &quot;CONFIRMED_FROM_DRAWING_TITLE&quot;,
  &quot;tag&quot;: &quot;AC-0244.0003&quot;,
  &quot;title_context&quot;: &quot;Fluxogramas típicos - casa de máquinas - fancoil&quot;,
  &quot;unverified_attributes&quot;: [
    &quot;instrument_tags&quot;,
    &quot;io_channels&quot;,
    &quot;setpoints&quot;,
    &quot;cause_effect_rows&quot;,
    &quot;datasheet_values&quot;
  ]
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;DE-0244.00-8210-944-TP7-003=D.pdf&quot;,
  &quot;page&quot;: 3,
  &quot;section&quot;: &quot;Título do desenho&quot;,
  &quot;source_id&quot;: &quot;PROJECT_PID&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="AUTOMACAO_DM_R00_05" data-entity="source" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="automacao-dm-r00-05" data-search="automacao-dm-r00-05 source automacao_dm_r00_05 e2_project_document review_required document_title: automação — diagrama de malha; revision: r00-05; table_title: símbolos de instrumentos; matrix: function_families: 4; physical_locations: 4; cells: 16; dimension_note: explicit_text: diâmetro = 12mm; explicitly_attached_to: instrumento_discreto_campo; generalization_to_all_cells: not_explicit_on_reference_sheet document: automação dm r00-05.pdf; page: 1; section: símbolos de instrumentos; source_id: automacao_dm_r00_05">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>

  <h3>AUTOMACAO-DM-R00-05</h3>
  <p>AUTOMAÇÃO — DIAGRAMA DE MALHA</p>

  <div class="deks-card-meta">AUTOMACAO_DM_R00_05 · source · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>

    <h2>AUTOMACAO-DM-R00-05</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-05ab16535d1ee88666b7</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-c1bb0237fbc5ef53</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-c1bb0237fbc5ef53.json</pre></td></tr><tr><th>Fonte</th><td><pre>AUTOMACAO_DM_R00_05</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>R00-05</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>source</pre></td></tr><tr><th>External ID</th><td><pre>AUTOMACAO-DM-R00-05</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;dimension_note&quot;: {
    &quot;explicit_text&quot;: &quot;DIÂMETRO = 12mm&quot;,
    &quot;explicitly_attached_to&quot;: &quot;instrumento_discreto_campo&quot;,
    &quot;generalization_to_all_cells&quot;: &quot;not_explicit_on_reference_sheet&quot;
  },
  &quot;document_title&quot;: &quot;AUTOMAÇÃO — DIAGRAMA DE MALHA&quot;,
  &quot;matrix&quot;: {
    &quot;cells&quot;: 16,
    &quot;function_families&quot;: 4,
    &quot;physical_locations&quot;: 4
  },
  &quot;revision&quot;: &quot;R00-05&quot;,
  &quot;table_title&quot;: &quot;SÍMBOLOS DE INSTRUMENTOS&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;document&quot;: &quot;AUTOMAÇÃO DM R00-05.pdf&quot;,
  &quot;page&quot;: 1,
  &quot;section&quot;: &quot;Símbolos de instrumentos&quot;,
  &quot;source_id&quot;: &quot;AUTOMACAO_DM_R00_05&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="AUTOMACAO_DM_R00_05" data-entity="symbol" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="dm-instrumento_discreto-campo" data-search="dm-instrumento_discreto-campo symbol automacao_dm_r00_05 e2_project_document review_required standard: automação dm r00-05; symbol_family: instrumento_discreto; base_geometry: circle; physical_location: field; location_marking: none; matrix_cell: instrumento_discreto__field; geometry_policy: exact_reference_geometry_no_approximation_or_deformation; explicit_dimension_mm: 12; dimension_evidence: explicit_on_sheet document: automação dm r00-05.pdf; page: 1; section: símbolos de instrumentos; row: instrumento_discreto; column: field; source_id: automacao_dm_r00_05">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>
  <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><circle cx="50" cy="50" r="28" fill="none" stroke="currentColor" stroke-width="3"/></svg>
  <h3>DM-INSTRUMENTO_DISCRETO-CAMPO</h3>
  <p>AUTOMAÇÃO DM R00-05</p>
  <p class="deks-dimension-note">Dimensão explícita na folha: 12 mm.</p>
  <div class="deks-card-meta">AUTOMACAO_DM_R00_05 · symbol · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>
    <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><circle cx="50" cy="50" r="28" fill="none" stroke="currentColor" stroke-width="3"/></svg>
    <h2>DM-INSTRUMENTO_DISCRETO-CAMPO</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-bbe0748eb030b2f094d3</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-c1bb0237fbc5ef53</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-c1bb0237fbc5ef53.json</pre></td></tr><tr><th>Fonte</th><td><pre>AUTOMACAO_DM_R00_05</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>R00-05</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>symbol</pre></td></tr><tr><th>External ID</th><td><pre>DM-INSTRUMENTO_DISCRETO-CAMPO</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;base_geometry&quot;: &quot;circle&quot;,
  &quot;dimension_evidence&quot;: &quot;explicit_on_sheet&quot;,
  &quot;explicit_dimension_mm&quot;: 12,
  &quot;geometry_policy&quot;: &quot;exact_reference_geometry_no_approximation_or_deformation&quot;,
  &quot;location_marking&quot;: &quot;none&quot;,
  &quot;matrix_cell&quot;: &quot;instrumento_discreto__field&quot;,
  &quot;physical_location&quot;: &quot;field&quot;,
  &quot;standard&quot;: &quot;AUTOMAÇÃO DM R00-05&quot;,
  &quot;symbol_family&quot;: &quot;instrumento_discreto&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;column&quot;: &quot;field&quot;,
  &quot;document&quot;: &quot;AUTOMAÇÃO DM R00-05.pdf&quot;,
  &quot;page&quot;: 1,
  &quot;row&quot;: &quot;instrumento_discreto&quot;,
  &quot;section&quot;: &quot;Símbolos de instrumentos&quot;,
  &quot;source_id&quot;: &quot;AUTOMACAO_DM_R00_05&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="AUTOMACAO_DM_R00_05" data-entity="symbol" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="dm-instrumento_discreto-painel_principal" data-search="dm-instrumento_discreto-painel_principal symbol automacao_dm_r00_05 e2_project_document review_required standard: automação dm r00-05; symbol_family: instrumento_discreto; base_geometry: circle; physical_location: main_control_panel; location_marking: one_solid_horizontal_bar; matrix_cell: instrumento_discreto__main_control_panel; geometry_policy: exact_reference_geometry_no_approximation_or_deformation; explicit_dimension_mm: ; dimension_evidence: not_explicit_for_this_cell_on_reference_sheet document: automação dm r00-05.pdf; page: 1; section: símbolos de instrumentos; row: instrumento_discreto; column: main_control_panel; source_id: automacao_dm_r00_05">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>
  <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><circle cx="50" cy="50" r="28" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="50" x2="82" y2="50" stroke="currentColor" stroke-width="3"/></svg>
  <h3>DM-INSTRUMENTO_DISCRETO-PAINEL_PRINCIPAL</h3>
  <p>AUTOMAÇÃO DM R00-05</p>
  <p class="deks-dimension-note">Dimensão não explícita para esta célula na folha de referência.</p>
  <div class="deks-card-meta">AUTOMACAO_DM_R00_05 · symbol · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>
    <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><circle cx="50" cy="50" r="28" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="50" x2="82" y2="50" stroke="currentColor" stroke-width="3"/></svg>
    <h2>DM-INSTRUMENTO_DISCRETO-PAINEL_PRINCIPAL</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-7b0eed13cf3ae69d8776</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-c1bb0237fbc5ef53</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-c1bb0237fbc5ef53.json</pre></td></tr><tr><th>Fonte</th><td><pre>AUTOMACAO_DM_R00_05</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>R00-05</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>symbol</pre></td></tr><tr><th>External ID</th><td><pre>DM-INSTRUMENTO_DISCRETO-PAINEL_PRINCIPAL</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;base_geometry&quot;: &quot;circle&quot;,
  &quot;dimension_evidence&quot;: &quot;not_explicit_for_this_cell_on_reference_sheet&quot;,
  &quot;explicit_dimension_mm&quot;: null,
  &quot;geometry_policy&quot;: &quot;exact_reference_geometry_no_approximation_or_deformation&quot;,
  &quot;location_marking&quot;: &quot;one_solid_horizontal_bar&quot;,
  &quot;matrix_cell&quot;: &quot;instrumento_discreto__main_control_panel&quot;,
  &quot;physical_location&quot;: &quot;main_control_panel&quot;,
  &quot;standard&quot;: &quot;AUTOMAÇÃO DM R00-05&quot;,
  &quot;symbol_family&quot;: &quot;instrumento_discreto&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;column&quot;: &quot;main_control_panel&quot;,
  &quot;document&quot;: &quot;AUTOMAÇÃO DM R00-05.pdf&quot;,
  &quot;page&quot;: 1,
  &quot;row&quot;: &quot;instrumento_discreto&quot;,
  &quot;section&quot;: &quot;Símbolos de instrumentos&quot;,
  &quot;source_id&quot;: &quot;AUTOMACAO_DM_R00_05&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="AUTOMACAO_DM_R00_05" data-entity="symbol" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="dm-instrumento_discreto-atras_painel_principal" data-search="dm-instrumento_discreto-atras_painel_principal symbol automacao_dm_r00_05 e2_project_document review_required standard: automação dm r00-05; symbol_family: instrumento_discreto; base_geometry: circle; physical_location: behind_main_control_panel; location_marking: one_dashed_horizontal_bar; matrix_cell: instrumento_discreto__behind_main_control_panel; geometry_policy: exact_reference_geometry_no_approximation_or_deformation; explicit_dimension_mm: ; dimension_evidence: not_explicit_for_this_cell_on_reference_sheet document: automação dm r00-05.pdf; page: 1; section: símbolos de instrumentos; row: instrumento_discreto; column: behind_main_control_panel; source_id: automacao_dm_r00_05">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>
  <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><circle cx="50" cy="50" r="28" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="50" x2="82" y2="50" stroke="currentColor" stroke-width="3" stroke-dasharray="7 5"/></svg>
  <h3>DM-INSTRUMENTO_DISCRETO-ATRAS_PAINEL_PRINCIPAL</h3>
  <p>AUTOMAÇÃO DM R00-05</p>
  <p class="deks-dimension-note">Dimensão não explícita para esta célula na folha de referência.</p>
  <div class="deks-card-meta">AUTOMACAO_DM_R00_05 · symbol · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>
    <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><circle cx="50" cy="50" r="28" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="50" x2="82" y2="50" stroke="currentColor" stroke-width="3" stroke-dasharray="7 5"/></svg>
    <h2>DM-INSTRUMENTO_DISCRETO-ATRAS_PAINEL_PRINCIPAL</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-4b190b770225e17dc3e3</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-c1bb0237fbc5ef53</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-c1bb0237fbc5ef53.json</pre></td></tr><tr><th>Fonte</th><td><pre>AUTOMACAO_DM_R00_05</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>R00-05</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>symbol</pre></td></tr><tr><th>External ID</th><td><pre>DM-INSTRUMENTO_DISCRETO-ATRAS_PAINEL_PRINCIPAL</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;base_geometry&quot;: &quot;circle&quot;,
  &quot;dimension_evidence&quot;: &quot;not_explicit_for_this_cell_on_reference_sheet&quot;,
  &quot;explicit_dimension_mm&quot;: null,
  &quot;geometry_policy&quot;: &quot;exact_reference_geometry_no_approximation_or_deformation&quot;,
  &quot;location_marking&quot;: &quot;one_dashed_horizontal_bar&quot;,
  &quot;matrix_cell&quot;: &quot;instrumento_discreto__behind_main_control_panel&quot;,
  &quot;physical_location&quot;: &quot;behind_main_control_panel&quot;,
  &quot;standard&quot;: &quot;AUTOMAÇÃO DM R00-05&quot;,
  &quot;symbol_family&quot;: &quot;instrumento_discreto&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;column&quot;: &quot;behind_main_control_panel&quot;,
  &quot;document&quot;: &quot;AUTOMAÇÃO DM R00-05.pdf&quot;,
  &quot;page&quot;: 1,
  &quot;row&quot;: &quot;instrumento_discreto&quot;,
  &quot;section&quot;: &quot;Símbolos de instrumentos&quot;,
  &quot;source_id&quot;: &quot;AUTOMACAO_DM_R00_05&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="AUTOMACAO_DM_R00_05" data-entity="symbol" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="dm-instrumento_discreto-painel_local_equipamento" data-search="dm-instrumento_discreto-painel_local_equipamento symbol automacao_dm_r00_05 e2_project_document review_required standard: automação dm r00-05; symbol_family: instrumento_discreto; base_geometry: circle; physical_location: local_equipment_panel; location_marking: two_solid_horizontal_bars; matrix_cell: instrumento_discreto__local_equipment_panel; geometry_policy: exact_reference_geometry_no_approximation_or_deformation; explicit_dimension_mm: ; dimension_evidence: not_explicit_for_this_cell_on_reference_sheet document: automação dm r00-05.pdf; page: 1; section: símbolos de instrumentos; row: instrumento_discreto; column: local_equipment_panel; source_id: automacao_dm_r00_05">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>
  <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><circle cx="50" cy="50" r="28" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="44" x2="82" y2="44" stroke="currentColor" stroke-width="3"/><line x1="18" y1="56" x2="82" y2="56" stroke="currentColor" stroke-width="3"/></svg>
  <h3>DM-INSTRUMENTO_DISCRETO-PAINEL_LOCAL_EQUIPAMENTO</h3>
  <p>AUTOMAÇÃO DM R00-05</p>
  <p class="deks-dimension-note">Dimensão não explícita para esta célula na folha de referência.</p>
  <div class="deks-card-meta">AUTOMACAO_DM_R00_05 · symbol · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>
    <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><circle cx="50" cy="50" r="28" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="44" x2="82" y2="44" stroke="currentColor" stroke-width="3"/><line x1="18" y1="56" x2="82" y2="56" stroke="currentColor" stroke-width="3"/></svg>
    <h2>DM-INSTRUMENTO_DISCRETO-PAINEL_LOCAL_EQUIPAMENTO</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-d4263e9c9950467751e6</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-c1bb0237fbc5ef53</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-c1bb0237fbc5ef53.json</pre></td></tr><tr><th>Fonte</th><td><pre>AUTOMACAO_DM_R00_05</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>R00-05</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>symbol</pre></td></tr><tr><th>External ID</th><td><pre>DM-INSTRUMENTO_DISCRETO-PAINEL_LOCAL_EQUIPAMENTO</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;base_geometry&quot;: &quot;circle&quot;,
  &quot;dimension_evidence&quot;: &quot;not_explicit_for_this_cell_on_reference_sheet&quot;,
  &quot;explicit_dimension_mm&quot;: null,
  &quot;geometry_policy&quot;: &quot;exact_reference_geometry_no_approximation_or_deformation&quot;,
  &quot;location_marking&quot;: &quot;two_solid_horizontal_bars&quot;,
  &quot;matrix_cell&quot;: &quot;instrumento_discreto__local_equipment_panel&quot;,
  &quot;physical_location&quot;: &quot;local_equipment_panel&quot;,
  &quot;standard&quot;: &quot;AUTOMAÇÃO DM R00-05&quot;,
  &quot;symbol_family&quot;: &quot;instrumento_discreto&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;column&quot;: &quot;local_equipment_panel&quot;,
  &quot;document&quot;: &quot;AUTOMAÇÃO DM R00-05.pdf&quot;,
  &quot;page&quot;: 1,
  &quot;row&quot;: &quot;instrumento_discreto&quot;,
  &quot;section&quot;: &quot;Símbolos de instrumentos&quot;,
  &quot;source_id&quot;: &quot;AUTOMACAO_DM_R00_05&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="AUTOMACAO_DM_R00_05" data-entity="symbol" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="dm-display_compartilhado-campo" data-search="dm-display_compartilhado-campo symbol automacao_dm_r00_05 e2_project_document review_required standard: automação dm r00-05; symbol_family: display_compartilhado; base_geometry: circle_inside_square; physical_location: field; location_marking: none; matrix_cell: display_compartilhado__field; geometry_policy: exact_reference_geometry_no_approximation_or_deformation; explicit_dimension_mm: ; dimension_evidence: not_explicit_for_this_cell_on_reference_sheet document: automação dm r00-05.pdf; page: 1; section: símbolos de instrumentos; row: display_compartilhado; column: field; source_id: automacao_dm_r00_05">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>
  <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><rect x="18" y="18" width="64" height="64" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="50" cy="50" r="22" fill="none" stroke="currentColor" stroke-width="3"/></svg>
  <h3>DM-DISPLAY_COMPARTILHADO-CAMPO</h3>
  <p>AUTOMAÇÃO DM R00-05</p>
  <p class="deks-dimension-note">Dimensão não explícita para esta célula na folha de referência.</p>
  <div class="deks-card-meta">AUTOMACAO_DM_R00_05 · symbol · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>
    <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><rect x="18" y="18" width="64" height="64" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="50" cy="50" r="22" fill="none" stroke="currentColor" stroke-width="3"/></svg>
    <h2>DM-DISPLAY_COMPARTILHADO-CAMPO</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-592fd733b1dbf1abea40</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-c1bb0237fbc5ef53</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-c1bb0237fbc5ef53.json</pre></td></tr><tr><th>Fonte</th><td><pre>AUTOMACAO_DM_R00_05</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>R00-05</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>symbol</pre></td></tr><tr><th>External ID</th><td><pre>DM-DISPLAY_COMPARTILHADO-CAMPO</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;base_geometry&quot;: &quot;circle_inside_square&quot;,
  &quot;dimension_evidence&quot;: &quot;not_explicit_for_this_cell_on_reference_sheet&quot;,
  &quot;explicit_dimension_mm&quot;: null,
  &quot;geometry_policy&quot;: &quot;exact_reference_geometry_no_approximation_or_deformation&quot;,
  &quot;location_marking&quot;: &quot;none&quot;,
  &quot;matrix_cell&quot;: &quot;display_compartilhado__field&quot;,
  &quot;physical_location&quot;: &quot;field&quot;,
  &quot;standard&quot;: &quot;AUTOMAÇÃO DM R00-05&quot;,
  &quot;symbol_family&quot;: &quot;display_compartilhado&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;column&quot;: &quot;field&quot;,
  &quot;document&quot;: &quot;AUTOMAÇÃO DM R00-05.pdf&quot;,
  &quot;page&quot;: 1,
  &quot;row&quot;: &quot;display_compartilhado&quot;,
  &quot;section&quot;: &quot;Símbolos de instrumentos&quot;,
  &quot;source_id&quot;: &quot;AUTOMACAO_DM_R00_05&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="AUTOMACAO_DM_R00_05" data-entity="symbol" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="dm-display_compartilhado-painel_principal" data-search="dm-display_compartilhado-painel_principal symbol automacao_dm_r00_05 e2_project_document review_required standard: automação dm r00-05; symbol_family: display_compartilhado; base_geometry: circle_inside_square; physical_location: main_control_panel; location_marking: one_solid_horizontal_bar; matrix_cell: display_compartilhado__main_control_panel; geometry_policy: exact_reference_geometry_no_approximation_or_deformation; explicit_dimension_mm: ; dimension_evidence: not_explicit_for_this_cell_on_reference_sheet document: automação dm r00-05.pdf; page: 1; section: símbolos de instrumentos; row: display_compartilhado; column: main_control_panel; source_id: automacao_dm_r00_05">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>
  <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><rect x="18" y="18" width="64" height="64" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="50" cy="50" r="22" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="50" x2="82" y2="50" stroke="currentColor" stroke-width="3"/></svg>
  <h3>DM-DISPLAY_COMPARTILHADO-PAINEL_PRINCIPAL</h3>
  <p>AUTOMAÇÃO DM R00-05</p>
  <p class="deks-dimension-note">Dimensão não explícita para esta célula na folha de referência.</p>
  <div class="deks-card-meta">AUTOMACAO_DM_R00_05 · symbol · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>
    <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><rect x="18" y="18" width="64" height="64" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="50" cy="50" r="22" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="50" x2="82" y2="50" stroke="currentColor" stroke-width="3"/></svg>
    <h2>DM-DISPLAY_COMPARTILHADO-PAINEL_PRINCIPAL</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-b94400d74ee0f5fdd840</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-c1bb0237fbc5ef53</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-c1bb0237fbc5ef53.json</pre></td></tr><tr><th>Fonte</th><td><pre>AUTOMACAO_DM_R00_05</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>R00-05</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>symbol</pre></td></tr><tr><th>External ID</th><td><pre>DM-DISPLAY_COMPARTILHADO-PAINEL_PRINCIPAL</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;base_geometry&quot;: &quot;circle_inside_square&quot;,
  &quot;dimension_evidence&quot;: &quot;not_explicit_for_this_cell_on_reference_sheet&quot;,
  &quot;explicit_dimension_mm&quot;: null,
  &quot;geometry_policy&quot;: &quot;exact_reference_geometry_no_approximation_or_deformation&quot;,
  &quot;location_marking&quot;: &quot;one_solid_horizontal_bar&quot;,
  &quot;matrix_cell&quot;: &quot;display_compartilhado__main_control_panel&quot;,
  &quot;physical_location&quot;: &quot;main_control_panel&quot;,
  &quot;standard&quot;: &quot;AUTOMAÇÃO DM R00-05&quot;,
  &quot;symbol_family&quot;: &quot;display_compartilhado&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;column&quot;: &quot;main_control_panel&quot;,
  &quot;document&quot;: &quot;AUTOMAÇÃO DM R00-05.pdf&quot;,
  &quot;page&quot;: 1,
  &quot;row&quot;: &quot;display_compartilhado&quot;,
  &quot;section&quot;: &quot;Símbolos de instrumentos&quot;,
  &quot;source_id&quot;: &quot;AUTOMACAO_DM_R00_05&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="AUTOMACAO_DM_R00_05" data-entity="symbol" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="dm-display_compartilhado-atras_painel_principal" data-search="dm-display_compartilhado-atras_painel_principal symbol automacao_dm_r00_05 e2_project_document review_required standard: automação dm r00-05; symbol_family: display_compartilhado; base_geometry: circle_inside_square; physical_location: behind_main_control_panel; location_marking: one_dashed_horizontal_bar; matrix_cell: display_compartilhado__behind_main_control_panel; geometry_policy: exact_reference_geometry_no_approximation_or_deformation; explicit_dimension_mm: ; dimension_evidence: not_explicit_for_this_cell_on_reference_sheet document: automação dm r00-05.pdf; page: 1; section: símbolos de instrumentos; row: display_compartilhado; column: behind_main_control_panel; source_id: automacao_dm_r00_05">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>
  <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><rect x="18" y="18" width="64" height="64" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="50" cy="50" r="22" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="50" x2="82" y2="50" stroke="currentColor" stroke-width="3" stroke-dasharray="7 5"/></svg>
  <h3>DM-DISPLAY_COMPARTILHADO-ATRAS_PAINEL_PRINCIPAL</h3>
  <p>AUTOMAÇÃO DM R00-05</p>
  <p class="deks-dimension-note">Dimensão não explícita para esta célula na folha de referência.</p>
  <div class="deks-card-meta">AUTOMACAO_DM_R00_05 · symbol · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>
    <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><rect x="18" y="18" width="64" height="64" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="50" cy="50" r="22" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="50" x2="82" y2="50" stroke="currentColor" stroke-width="3" stroke-dasharray="7 5"/></svg>
    <h2>DM-DISPLAY_COMPARTILHADO-ATRAS_PAINEL_PRINCIPAL</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-9edafa1147e26182e5af</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-c1bb0237fbc5ef53</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-c1bb0237fbc5ef53.json</pre></td></tr><tr><th>Fonte</th><td><pre>AUTOMACAO_DM_R00_05</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>R00-05</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>symbol</pre></td></tr><tr><th>External ID</th><td><pre>DM-DISPLAY_COMPARTILHADO-ATRAS_PAINEL_PRINCIPAL</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;base_geometry&quot;: &quot;circle_inside_square&quot;,
  &quot;dimension_evidence&quot;: &quot;not_explicit_for_this_cell_on_reference_sheet&quot;,
  &quot;explicit_dimension_mm&quot;: null,
  &quot;geometry_policy&quot;: &quot;exact_reference_geometry_no_approximation_or_deformation&quot;,
  &quot;location_marking&quot;: &quot;one_dashed_horizontal_bar&quot;,
  &quot;matrix_cell&quot;: &quot;display_compartilhado__behind_main_control_panel&quot;,
  &quot;physical_location&quot;: &quot;behind_main_control_panel&quot;,
  &quot;standard&quot;: &quot;AUTOMAÇÃO DM R00-05&quot;,
  &quot;symbol_family&quot;: &quot;display_compartilhado&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;column&quot;: &quot;behind_main_control_panel&quot;,
  &quot;document&quot;: &quot;AUTOMAÇÃO DM R00-05.pdf&quot;,
  &quot;page&quot;: 1,
  &quot;row&quot;: &quot;display_compartilhado&quot;,
  &quot;section&quot;: &quot;Símbolos de instrumentos&quot;,
  &quot;source_id&quot;: &quot;AUTOMACAO_DM_R00_05&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="AUTOMACAO_DM_R00_05" data-entity="symbol" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="dm-display_compartilhado-painel_local_equipamento" data-search="dm-display_compartilhado-painel_local_equipamento symbol automacao_dm_r00_05 e2_project_document review_required standard: automação dm r00-05; symbol_family: display_compartilhado; base_geometry: circle_inside_square; physical_location: local_equipment_panel; location_marking: two_solid_horizontal_bars; matrix_cell: display_compartilhado__local_equipment_panel; geometry_policy: exact_reference_geometry_no_approximation_or_deformation; explicit_dimension_mm: ; dimension_evidence: not_explicit_for_this_cell_on_reference_sheet document: automação dm r00-05.pdf; page: 1; section: símbolos de instrumentos; row: display_compartilhado; column: local_equipment_panel; source_id: automacao_dm_r00_05">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>
  <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><rect x="18" y="18" width="64" height="64" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="50" cy="50" r="22" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="44" x2="82" y2="44" stroke="currentColor" stroke-width="3"/><line x1="18" y1="56" x2="82" y2="56" stroke="currentColor" stroke-width="3"/></svg>
  <h3>DM-DISPLAY_COMPARTILHADO-PAINEL_LOCAL_EQUIPAMENTO</h3>
  <p>AUTOMAÇÃO DM R00-05</p>
  <p class="deks-dimension-note">Dimensão não explícita para esta célula na folha de referência.</p>
  <div class="deks-card-meta">AUTOMACAO_DM_R00_05 · symbol · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>
    <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><rect x="18" y="18" width="64" height="64" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="50" cy="50" r="22" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="44" x2="82" y2="44" stroke="currentColor" stroke-width="3"/><line x1="18" y1="56" x2="82" y2="56" stroke="currentColor" stroke-width="3"/></svg>
    <h2>DM-DISPLAY_COMPARTILHADO-PAINEL_LOCAL_EQUIPAMENTO</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-a6db8d76872dd18425d3</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-c1bb0237fbc5ef53</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-c1bb0237fbc5ef53.json</pre></td></tr><tr><th>Fonte</th><td><pre>AUTOMACAO_DM_R00_05</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>R00-05</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>symbol</pre></td></tr><tr><th>External ID</th><td><pre>DM-DISPLAY_COMPARTILHADO-PAINEL_LOCAL_EQUIPAMENTO</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;base_geometry&quot;: &quot;circle_inside_square&quot;,
  &quot;dimension_evidence&quot;: &quot;not_explicit_for_this_cell_on_reference_sheet&quot;,
  &quot;explicit_dimension_mm&quot;: null,
  &quot;geometry_policy&quot;: &quot;exact_reference_geometry_no_approximation_or_deformation&quot;,
  &quot;location_marking&quot;: &quot;two_solid_horizontal_bars&quot;,
  &quot;matrix_cell&quot;: &quot;display_compartilhado__local_equipment_panel&quot;,
  &quot;physical_location&quot;: &quot;local_equipment_panel&quot;,
  &quot;standard&quot;: &quot;AUTOMAÇÃO DM R00-05&quot;,
  &quot;symbol_family&quot;: &quot;display_compartilhado&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;column&quot;: &quot;local_equipment_panel&quot;,
  &quot;document&quot;: &quot;AUTOMAÇÃO DM R00-05.pdf&quot;,
  &quot;page&quot;: 1,
  &quot;row&quot;: &quot;display_compartilhado&quot;,
  &quot;section&quot;: &quot;Símbolos de instrumentos&quot;,
  &quot;source_id&quot;: &quot;AUTOMACAO_DM_R00_05&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="AUTOMACAO_DM_R00_05" data-entity="symbol" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="dm-funcao_computador-campo" data-search="dm-funcao_computador-campo symbol automacao_dm_r00_05 e2_project_document review_required standard: automação dm r00-05; symbol_family: funcao_executada_no_computador; base_geometry: hexagon; physical_location: field; location_marking: none; matrix_cell: funcao_executada_no_computador__field; geometry_policy: exact_reference_geometry_no_approximation_or_deformation; explicit_dimension_mm: ; dimension_evidence: not_explicit_for_this_cell_on_reference_sheet document: automação dm r00-05.pdf; page: 1; section: símbolos de instrumentos; row: funcao_executada_no_computador; column: field; source_id: automacao_dm_r00_05">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>
  <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><polygon points="50,16 78,32 78,68 50,84 22,68 22,32" fill="none" stroke="currentColor" stroke-width="3"/></svg>
  <h3>DM-FUNCAO_COMPUTADOR-CAMPO</h3>
  <p>AUTOMAÇÃO DM R00-05</p>
  <p class="deks-dimension-note">Dimensão não explícita para esta célula na folha de referência.</p>
  <div class="deks-card-meta">AUTOMACAO_DM_R00_05 · symbol · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>
    <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><polygon points="50,16 78,32 78,68 50,84 22,68 22,32" fill="none" stroke="currentColor" stroke-width="3"/></svg>
    <h2>DM-FUNCAO_COMPUTADOR-CAMPO</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-11a7f257460004354149</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-c1bb0237fbc5ef53</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-c1bb0237fbc5ef53.json</pre></td></tr><tr><th>Fonte</th><td><pre>AUTOMACAO_DM_R00_05</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>R00-05</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>symbol</pre></td></tr><tr><th>External ID</th><td><pre>DM-FUNCAO_COMPUTADOR-CAMPO</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;base_geometry&quot;: &quot;hexagon&quot;,
  &quot;dimension_evidence&quot;: &quot;not_explicit_for_this_cell_on_reference_sheet&quot;,
  &quot;explicit_dimension_mm&quot;: null,
  &quot;geometry_policy&quot;: &quot;exact_reference_geometry_no_approximation_or_deformation&quot;,
  &quot;location_marking&quot;: &quot;none&quot;,
  &quot;matrix_cell&quot;: &quot;funcao_executada_no_computador__field&quot;,
  &quot;physical_location&quot;: &quot;field&quot;,
  &quot;standard&quot;: &quot;AUTOMAÇÃO DM R00-05&quot;,
  &quot;symbol_family&quot;: &quot;funcao_executada_no_computador&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;column&quot;: &quot;field&quot;,
  &quot;document&quot;: &quot;AUTOMAÇÃO DM R00-05.pdf&quot;,
  &quot;page&quot;: 1,
  &quot;row&quot;: &quot;funcao_executada_no_computador&quot;,
  &quot;section&quot;: &quot;Símbolos de instrumentos&quot;,
  &quot;source_id&quot;: &quot;AUTOMACAO_DM_R00_05&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="AUTOMACAO_DM_R00_05" data-entity="symbol" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="dm-funcao_computador-painel_principal" data-search="dm-funcao_computador-painel_principal symbol automacao_dm_r00_05 e2_project_document review_required standard: automação dm r00-05; symbol_family: funcao_executada_no_computador; base_geometry: hexagon; physical_location: main_control_panel; location_marking: one_solid_horizontal_bar; matrix_cell: funcao_executada_no_computador__main_control_panel; geometry_policy: exact_reference_geometry_no_approximation_or_deformation; explicit_dimension_mm: ; dimension_evidence: not_explicit_for_this_cell_on_reference_sheet document: automação dm r00-05.pdf; page: 1; section: símbolos de instrumentos; row: funcao_executada_no_computador; column: main_control_panel; source_id: automacao_dm_r00_05">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>
  <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><polygon points="50,16 78,32 78,68 50,84 22,68 22,32" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="50" x2="82" y2="50" stroke="currentColor" stroke-width="3"/></svg>
  <h3>DM-FUNCAO_COMPUTADOR-PAINEL_PRINCIPAL</h3>
  <p>AUTOMAÇÃO DM R00-05</p>
  <p class="deks-dimension-note">Dimensão não explícita para esta célula na folha de referência.</p>
  <div class="deks-card-meta">AUTOMACAO_DM_R00_05 · symbol · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>
    <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><polygon points="50,16 78,32 78,68 50,84 22,68 22,32" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="50" x2="82" y2="50" stroke="currentColor" stroke-width="3"/></svg>
    <h2>DM-FUNCAO_COMPUTADOR-PAINEL_PRINCIPAL</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-b73e55277b3b2686a3fd</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-c1bb0237fbc5ef53</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-c1bb0237fbc5ef53.json</pre></td></tr><tr><th>Fonte</th><td><pre>AUTOMACAO_DM_R00_05</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>R00-05</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>symbol</pre></td></tr><tr><th>External ID</th><td><pre>DM-FUNCAO_COMPUTADOR-PAINEL_PRINCIPAL</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;base_geometry&quot;: &quot;hexagon&quot;,
  &quot;dimension_evidence&quot;: &quot;not_explicit_for_this_cell_on_reference_sheet&quot;,
  &quot;explicit_dimension_mm&quot;: null,
  &quot;geometry_policy&quot;: &quot;exact_reference_geometry_no_approximation_or_deformation&quot;,
  &quot;location_marking&quot;: &quot;one_solid_horizontal_bar&quot;,
  &quot;matrix_cell&quot;: &quot;funcao_executada_no_computador__main_control_panel&quot;,
  &quot;physical_location&quot;: &quot;main_control_panel&quot;,
  &quot;standard&quot;: &quot;AUTOMAÇÃO DM R00-05&quot;,
  &quot;symbol_family&quot;: &quot;funcao_executada_no_computador&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;column&quot;: &quot;main_control_panel&quot;,
  &quot;document&quot;: &quot;AUTOMAÇÃO DM R00-05.pdf&quot;,
  &quot;page&quot;: 1,
  &quot;row&quot;: &quot;funcao_executada_no_computador&quot;,
  &quot;section&quot;: &quot;Símbolos de instrumentos&quot;,
  &quot;source_id&quot;: &quot;AUTOMACAO_DM_R00_05&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="AUTOMACAO_DM_R00_05" data-entity="symbol" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="dm-funcao_computador-atras_painel_principal" data-search="dm-funcao_computador-atras_painel_principal symbol automacao_dm_r00_05 e2_project_document review_required standard: automação dm r00-05; symbol_family: funcao_executada_no_computador; base_geometry: hexagon; physical_location: behind_main_control_panel; location_marking: one_dashed_horizontal_bar; matrix_cell: funcao_executada_no_computador__behind_main_control_panel; geometry_policy: exact_reference_geometry_no_approximation_or_deformation; explicit_dimension_mm: ; dimension_evidence: not_explicit_for_this_cell_on_reference_sheet document: automação dm r00-05.pdf; page: 1; section: símbolos de instrumentos; row: funcao_executada_no_computador; column: behind_main_control_panel; source_id: automacao_dm_r00_05">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>
  <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><polygon points="50,16 78,32 78,68 50,84 22,68 22,32" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="50" x2="82" y2="50" stroke="currentColor" stroke-width="3" stroke-dasharray="7 5"/></svg>
  <h3>DM-FUNCAO_COMPUTADOR-ATRAS_PAINEL_PRINCIPAL</h3>
  <p>AUTOMAÇÃO DM R00-05</p>
  <p class="deks-dimension-note">Dimensão não explícita para esta célula na folha de referência.</p>
  <div class="deks-card-meta">AUTOMACAO_DM_R00_05 · symbol · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>
    <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><polygon points="50,16 78,32 78,68 50,84 22,68 22,32" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="50" x2="82" y2="50" stroke="currentColor" stroke-width="3" stroke-dasharray="7 5"/></svg>
    <h2>DM-FUNCAO_COMPUTADOR-ATRAS_PAINEL_PRINCIPAL</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-d30f6503a9caa712c994</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-c1bb0237fbc5ef53</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-c1bb0237fbc5ef53.json</pre></td></tr><tr><th>Fonte</th><td><pre>AUTOMACAO_DM_R00_05</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>R00-05</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>symbol</pre></td></tr><tr><th>External ID</th><td><pre>DM-FUNCAO_COMPUTADOR-ATRAS_PAINEL_PRINCIPAL</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;base_geometry&quot;: &quot;hexagon&quot;,
  &quot;dimension_evidence&quot;: &quot;not_explicit_for_this_cell_on_reference_sheet&quot;,
  &quot;explicit_dimension_mm&quot;: null,
  &quot;geometry_policy&quot;: &quot;exact_reference_geometry_no_approximation_or_deformation&quot;,
  &quot;location_marking&quot;: &quot;one_dashed_horizontal_bar&quot;,
  &quot;matrix_cell&quot;: &quot;funcao_executada_no_computador__behind_main_control_panel&quot;,
  &quot;physical_location&quot;: &quot;behind_main_control_panel&quot;,
  &quot;standard&quot;: &quot;AUTOMAÇÃO DM R00-05&quot;,
  &quot;symbol_family&quot;: &quot;funcao_executada_no_computador&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;column&quot;: &quot;behind_main_control_panel&quot;,
  &quot;document&quot;: &quot;AUTOMAÇÃO DM R00-05.pdf&quot;,
  &quot;page&quot;: 1,
  &quot;row&quot;: &quot;funcao_executada_no_computador&quot;,
  &quot;section&quot;: &quot;Símbolos de instrumentos&quot;,
  &quot;source_id&quot;: &quot;AUTOMACAO_DM_R00_05&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="AUTOMACAO_DM_R00_05" data-entity="symbol" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="dm-funcao_computador-painel_local_equipamento" data-search="dm-funcao_computador-painel_local_equipamento symbol automacao_dm_r00_05 e2_project_document review_required standard: automação dm r00-05; symbol_family: funcao_executada_no_computador; base_geometry: hexagon; physical_location: local_equipment_panel; location_marking: two_solid_horizontal_bars; matrix_cell: funcao_executada_no_computador__local_equipment_panel; geometry_policy: exact_reference_geometry_no_approximation_or_deformation; explicit_dimension_mm: ; dimension_evidence: not_explicit_for_this_cell_on_reference_sheet document: automação dm r00-05.pdf; page: 1; section: símbolos de instrumentos; row: funcao_executada_no_computador; column: local_equipment_panel; source_id: automacao_dm_r00_05">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>
  <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><polygon points="50,16 78,32 78,68 50,84 22,68 22,32" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="44" x2="82" y2="44" stroke="currentColor" stroke-width="3"/><line x1="18" y1="56" x2="82" y2="56" stroke="currentColor" stroke-width="3"/></svg>
  <h3>DM-FUNCAO_COMPUTADOR-PAINEL_LOCAL_EQUIPAMENTO</h3>
  <p>AUTOMAÇÃO DM R00-05</p>
  <p class="deks-dimension-note">Dimensão não explícita para esta célula na folha de referência.</p>
  <div class="deks-card-meta">AUTOMACAO_DM_R00_05 · symbol · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>
    <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><polygon points="50,16 78,32 78,68 50,84 22,68 22,32" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="44" x2="82" y2="44" stroke="currentColor" stroke-width="3"/><line x1="18" y1="56" x2="82" y2="56" stroke="currentColor" stroke-width="3"/></svg>
    <h2>DM-FUNCAO_COMPUTADOR-PAINEL_LOCAL_EQUIPAMENTO</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-ad87c112a565d82466e5</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-c1bb0237fbc5ef53</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-c1bb0237fbc5ef53.json</pre></td></tr><tr><th>Fonte</th><td><pre>AUTOMACAO_DM_R00_05</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>R00-05</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>symbol</pre></td></tr><tr><th>External ID</th><td><pre>DM-FUNCAO_COMPUTADOR-PAINEL_LOCAL_EQUIPAMENTO</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;base_geometry&quot;: &quot;hexagon&quot;,
  &quot;dimension_evidence&quot;: &quot;not_explicit_for_this_cell_on_reference_sheet&quot;,
  &quot;explicit_dimension_mm&quot;: null,
  &quot;geometry_policy&quot;: &quot;exact_reference_geometry_no_approximation_or_deformation&quot;,
  &quot;location_marking&quot;: &quot;two_solid_horizontal_bars&quot;,
  &quot;matrix_cell&quot;: &quot;funcao_executada_no_computador__local_equipment_panel&quot;,
  &quot;physical_location&quot;: &quot;local_equipment_panel&quot;,
  &quot;standard&quot;: &quot;AUTOMAÇÃO DM R00-05&quot;,
  &quot;symbol_family&quot;: &quot;funcao_executada_no_computador&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;column&quot;: &quot;local_equipment_panel&quot;,
  &quot;document&quot;: &quot;AUTOMAÇÃO DM R00-05.pdf&quot;,
  &quot;page&quot;: 1,
  &quot;row&quot;: &quot;funcao_executada_no_computador&quot;,
  &quot;section&quot;: &quot;Símbolos de instrumentos&quot;,
  &quot;source_id&quot;: &quot;AUTOMACAO_DM_R00_05&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="AUTOMACAO_DM_R00_05" data-entity="symbol" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="dm-plc-campo" data-search="dm-plc-campo symbol automacao_dm_r00_05 e2_project_document review_required standard: automação dm r00-05; symbol_family: plc; base_geometry: diamond_inside_square; physical_location: field; location_marking: none; matrix_cell: plc__field; geometry_policy: exact_reference_geometry_no_approximation_or_deformation; explicit_dimension_mm: ; dimension_evidence: not_explicit_for_this_cell_on_reference_sheet document: automação dm r00-05.pdf; page: 1; section: símbolos de instrumentos; row: plc; column: field; source_id: automacao_dm_r00_05">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>
  <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><rect x="18" y="18" width="64" height="64" fill="none" stroke="currentColor" stroke-width="3"/><polygon points="50,26 74,50 50,74 26,50" fill="none" stroke="currentColor" stroke-width="3"/></svg>
  <h3>DM-PLC-CAMPO</h3>
  <p>AUTOMAÇÃO DM R00-05</p>
  <p class="deks-dimension-note">Dimensão não explícita para esta célula na folha de referência.</p>
  <div class="deks-card-meta">AUTOMACAO_DM_R00_05 · symbol · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>
    <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><rect x="18" y="18" width="64" height="64" fill="none" stroke="currentColor" stroke-width="3"/><polygon points="50,26 74,50 50,74 26,50" fill="none" stroke="currentColor" stroke-width="3"/></svg>
    <h2>DM-PLC-CAMPO</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-c402040be48f01bee316</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-c1bb0237fbc5ef53</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-c1bb0237fbc5ef53.json</pre></td></tr><tr><th>Fonte</th><td><pre>AUTOMACAO_DM_R00_05</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>R00-05</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>symbol</pre></td></tr><tr><th>External ID</th><td><pre>DM-PLC-CAMPO</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;base_geometry&quot;: &quot;diamond_inside_square&quot;,
  &quot;dimension_evidence&quot;: &quot;not_explicit_for_this_cell_on_reference_sheet&quot;,
  &quot;explicit_dimension_mm&quot;: null,
  &quot;geometry_policy&quot;: &quot;exact_reference_geometry_no_approximation_or_deformation&quot;,
  &quot;location_marking&quot;: &quot;none&quot;,
  &quot;matrix_cell&quot;: &quot;plc__field&quot;,
  &quot;physical_location&quot;: &quot;field&quot;,
  &quot;standard&quot;: &quot;AUTOMAÇÃO DM R00-05&quot;,
  &quot;symbol_family&quot;: &quot;plc&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;column&quot;: &quot;field&quot;,
  &quot;document&quot;: &quot;AUTOMAÇÃO DM R00-05.pdf&quot;,
  &quot;page&quot;: 1,
  &quot;row&quot;: &quot;plc&quot;,
  &quot;section&quot;: &quot;Símbolos de instrumentos&quot;,
  &quot;source_id&quot;: &quot;AUTOMACAO_DM_R00_05&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="AUTOMACAO_DM_R00_05" data-entity="symbol" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="dm-plc-painel_principal" data-search="dm-plc-painel_principal symbol automacao_dm_r00_05 e2_project_document review_required standard: automação dm r00-05; symbol_family: plc; base_geometry: diamond_inside_square; physical_location: main_control_panel; location_marking: one_solid_horizontal_bar; matrix_cell: plc__main_control_panel; geometry_policy: exact_reference_geometry_no_approximation_or_deformation; explicit_dimension_mm: ; dimension_evidence: not_explicit_for_this_cell_on_reference_sheet document: automação dm r00-05.pdf; page: 1; section: símbolos de instrumentos; row: plc; column: main_control_panel; source_id: automacao_dm_r00_05">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>
  <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><rect x="18" y="18" width="64" height="64" fill="none" stroke="currentColor" stroke-width="3"/><polygon points="50,26 74,50 50,74 26,50" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="50" x2="82" y2="50" stroke="currentColor" stroke-width="3"/></svg>
  <h3>DM-PLC-PAINEL_PRINCIPAL</h3>
  <p>AUTOMAÇÃO DM R00-05</p>
  <p class="deks-dimension-note">Dimensão não explícita para esta célula na folha de referência.</p>
  <div class="deks-card-meta">AUTOMACAO_DM_R00_05 · symbol · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>
    <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><rect x="18" y="18" width="64" height="64" fill="none" stroke="currentColor" stroke-width="3"/><polygon points="50,26 74,50 50,74 26,50" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="50" x2="82" y2="50" stroke="currentColor" stroke-width="3"/></svg>
    <h2>DM-PLC-PAINEL_PRINCIPAL</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-2d462a5f5537cb3d7540</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-c1bb0237fbc5ef53</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-c1bb0237fbc5ef53.json</pre></td></tr><tr><th>Fonte</th><td><pre>AUTOMACAO_DM_R00_05</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>R00-05</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>symbol</pre></td></tr><tr><th>External ID</th><td><pre>DM-PLC-PAINEL_PRINCIPAL</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;base_geometry&quot;: &quot;diamond_inside_square&quot;,
  &quot;dimension_evidence&quot;: &quot;not_explicit_for_this_cell_on_reference_sheet&quot;,
  &quot;explicit_dimension_mm&quot;: null,
  &quot;geometry_policy&quot;: &quot;exact_reference_geometry_no_approximation_or_deformation&quot;,
  &quot;location_marking&quot;: &quot;one_solid_horizontal_bar&quot;,
  &quot;matrix_cell&quot;: &quot;plc__main_control_panel&quot;,
  &quot;physical_location&quot;: &quot;main_control_panel&quot;,
  &quot;standard&quot;: &quot;AUTOMAÇÃO DM R00-05&quot;,
  &quot;symbol_family&quot;: &quot;plc&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;column&quot;: &quot;main_control_panel&quot;,
  &quot;document&quot;: &quot;AUTOMAÇÃO DM R00-05.pdf&quot;,
  &quot;page&quot;: 1,
  &quot;row&quot;: &quot;plc&quot;,
  &quot;section&quot;: &quot;Símbolos de instrumentos&quot;,
  &quot;source_id&quot;: &quot;AUTOMACAO_DM_R00_05&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="AUTOMACAO_DM_R00_05" data-entity="symbol" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="dm-plc-atras_painel_principal" data-search="dm-plc-atras_painel_principal symbol automacao_dm_r00_05 e2_project_document review_required standard: automação dm r00-05; symbol_family: plc; base_geometry: diamond_inside_square; physical_location: behind_main_control_panel; location_marking: one_dashed_horizontal_bar; matrix_cell: plc__behind_main_control_panel; geometry_policy: exact_reference_geometry_no_approximation_or_deformation; explicit_dimension_mm: ; dimension_evidence: not_explicit_for_this_cell_on_reference_sheet document: automação dm r00-05.pdf; page: 1; section: símbolos de instrumentos; row: plc; column: behind_main_control_panel; source_id: automacao_dm_r00_05">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>
  <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><rect x="18" y="18" width="64" height="64" fill="none" stroke="currentColor" stroke-width="3"/><polygon points="50,26 74,50 50,74 26,50" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="50" x2="82" y2="50" stroke="currentColor" stroke-width="3" stroke-dasharray="7 5"/></svg>
  <h3>DM-PLC-ATRAS_PAINEL_PRINCIPAL</h3>
  <p>AUTOMAÇÃO DM R00-05</p>
  <p class="deks-dimension-note">Dimensão não explícita para esta célula na folha de referência.</p>
  <div class="deks-card-meta">AUTOMACAO_DM_R00_05 · symbol · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>
    <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><rect x="18" y="18" width="64" height="64" fill="none" stroke="currentColor" stroke-width="3"/><polygon points="50,26 74,50 50,74 26,50" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="50" x2="82" y2="50" stroke="currentColor" stroke-width="3" stroke-dasharray="7 5"/></svg>
    <h2>DM-PLC-ATRAS_PAINEL_PRINCIPAL</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-9a6d0d804129d1a65107</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-c1bb0237fbc5ef53</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-c1bb0237fbc5ef53.json</pre></td></tr><tr><th>Fonte</th><td><pre>AUTOMACAO_DM_R00_05</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>R00-05</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>symbol</pre></td></tr><tr><th>External ID</th><td><pre>DM-PLC-ATRAS_PAINEL_PRINCIPAL</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;base_geometry&quot;: &quot;diamond_inside_square&quot;,
  &quot;dimension_evidence&quot;: &quot;not_explicit_for_this_cell_on_reference_sheet&quot;,
  &quot;explicit_dimension_mm&quot;: null,
  &quot;geometry_policy&quot;: &quot;exact_reference_geometry_no_approximation_or_deformation&quot;,
  &quot;location_marking&quot;: &quot;one_dashed_horizontal_bar&quot;,
  &quot;matrix_cell&quot;: &quot;plc__behind_main_control_panel&quot;,
  &quot;physical_location&quot;: &quot;behind_main_control_panel&quot;,
  &quot;standard&quot;: &quot;AUTOMAÇÃO DM R00-05&quot;,
  &quot;symbol_family&quot;: &quot;plc&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;column&quot;: &quot;behind_main_control_panel&quot;,
  &quot;document&quot;: &quot;AUTOMAÇÃO DM R00-05.pdf&quot;,
  &quot;page&quot;: 1,
  &quot;row&quot;: &quot;plc&quot;,
  &quot;section&quot;: &quot;Símbolos de instrumentos&quot;,
  &quot;source_id&quot;: &quot;AUTOMACAO_DM_R00_05&quot;
}</pre></td></tr></table>
  </template>
</article>
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="AUTOMACAO_DM_R00_05" data-entity="symbol" data-status="REVIEW_REQUIRED" data-evidence="E2_PROJECT_DOCUMENT" data-title="dm-plc-painel_local_equipamento" data-search="dm-plc-painel_local_equipamento symbol automacao_dm_r00_05 e2_project_document review_required standard: automação dm r00-05; symbol_family: plc; base_geometry: diamond_inside_square; physical_location: local_equipment_panel; location_marking: two_solid_horizontal_bars; matrix_cell: plc__local_equipment_panel; geometry_policy: exact_reference_geometry_no_approximation_or_deformation; explicit_dimension_mm: ; dimension_evidence: not_explicit_for_this_cell_on_reference_sheet document: automação dm r00-05.pdf; page: 1; section: símbolos de instrumentos; row: plc; column: local_equipment_panel; source_id: automacao_dm_r00_05">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">E2_PROJECT_DOCUMENT</span></div>
  <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><rect x="18" y="18" width="64" height="64" fill="none" stroke="currentColor" stroke-width="3"/><polygon points="50,26 74,50 50,74 26,50" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="44" x2="82" y2="44" stroke="currentColor" stroke-width="3"/><line x1="18" y1="56" x2="82" y2="56" stroke="currentColor" stroke-width="3"/></svg>
  <h3>DM-PLC-PAINEL_LOCAL_EQUIPAMENTO</h3>
  <p>AUTOMAÇÃO DM R00-05</p>
  <p class="deks-dimension-note">Dimensão não explícita para esta célula na folha de referência.</p>
  <div class="deks-card-meta">AUTOMACAO_DM_R00_05 · symbol · REVIEW_REQUIRED</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>
    <svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo"><rect x="18" y="18" width="64" height="64" fill="none" stroke="currentColor" stroke-width="3"/><polygon points="50,26 74,50 50,74 26,50" fill="none" stroke="currentColor" stroke-width="3"/><line x1="18" y1="44" x2="82" y2="44" stroke="currentColor" stroke-width="3"/><line x1="18" y1="56" x2="82" y2="56" stroke="currentColor" stroke-width="3"/></svg>
    <h2>DM-PLC-PAINEL_LOCAL_EQUIPAMENTO</h2>
    <table class="deks-detail-table"><tr><th>Ingestion ID</th><td><pre>ING-2a37d35ba5cd42274d53</pre></td></tr><tr><th>Batch</th><td><pre>BATCH-c1bb0237fbc5ef53</pre></td></tr><tr><th>Arquivo do batch</th><td><pre>BATCH-c1bb0237fbc5ef53.json</pre></td></tr><tr><th>Fonte</th><td><pre>AUTOMACAO_DM_R00_05</pre></td></tr><tr><th>Revisão da fonte</th><td><pre>R00-05</pre></td></tr><tr><th>Tipo de entidade</th><td><pre>symbol</pre></td></tr><tr><th>External ID</th><td><pre>DM-PLC-PAINEL_LOCAL_EQUIPAMENTO</pre></td></tr><tr><th>Classe de evidência</th><td><pre>E2_PROJECT_DOCUMENT</pre></td></tr><tr><th>Review status</th><td><pre>REVIEW_REQUIRED</pre></td></tr><tr><th>Auto-promoted</th><td><pre>False</pre></td></tr><tr><th>Payload</th><td><pre>{
  &quot;base_geometry&quot;: &quot;diamond_inside_square&quot;,
  &quot;dimension_evidence&quot;: &quot;not_explicit_for_this_cell_on_reference_sheet&quot;,
  &quot;explicit_dimension_mm&quot;: null,
  &quot;geometry_policy&quot;: &quot;exact_reference_geometry_no_approximation_or_deformation&quot;,
  &quot;location_marking&quot;: &quot;two_solid_horizontal_bars&quot;,
  &quot;matrix_cell&quot;: &quot;plc__local_equipment_panel&quot;,
  &quot;physical_location&quot;: &quot;local_equipment_panel&quot;,
  &quot;standard&quot;: &quot;AUTOMAÇÃO DM R00-05&quot;,
  &quot;symbol_family&quot;: &quot;plc&quot;
}</pre></td></tr><tr><th>Proveniência</th><td><pre>{
  &quot;column&quot;: &quot;local_equipment_panel&quot;,
  &quot;document&quot;: &quot;AUTOMAÇÃO DM R00-05.pdf&quot;,
  &quot;page&quot;: 1,
  &quot;row&quot;: &quot;plc&quot;,
  &quot;section&quot;: &quot;Símbolos de instrumentos&quot;,
  &quot;source_id&quot;: &quot;AUTOMACAO_DM_R00_05&quot;
}</pre></td></tr></table>
  </template>
</article>
</div>

<div id="deks-glossary-empty" class="deks-empty-state" hidden>Nenhum registro corresponde aos filtros selecionados.</div>

<aside id="deks-detail-panel" class="deks-detail-panel" hidden aria-live="polite">
  <div class="deks-detail-panel-toolbar"><button id="deks-detail-close" type="button" aria-label="Fechar ficha">Fechar</button></div>
  <div id="deks-detail-content"></div>
</aside>

## Fontes ainda bloqueadas

<ul>
<li><strong>Instrument Index</strong> — REGISTERED_PENDING_FILE</li><li><strong>I/O List</strong> — REGISTERED_PENDING_FILE</li><li><strong>Cause &amp; Effect / Matriz de Intertravamentos</strong> — REGISTERED_PENDING_FILE</li><li><strong>Datasheets de Engenharia</strong> — REGISTERED_PENDING_FILE</li>
</ul>

!!! warning "Dados pendentes"
    Instrument Index/I/O, C&amp;E e datasheets só entram no glossário interativo quando seus arquivos técnicos autônomos forem ingeridos. Até lá: **PENDENTE — NÃO HÁ EVIDÊNCIA SUFICIENTE PARA DEFINIR.**
