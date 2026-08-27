# Referência versionada do pipeline de agentes v4.5
# Implementação operacional mantida no pacote local AUTOMAÇÃO_Governanca_Engenharia_v4_5.

AGENTS = [
    "DatacenterStructureAgent",
    "DocumentUnderstandingAgent",
    "EvidenceTraceabilityAgent",
    "DocumentLayoutLockAgent",
    "DataSheetConsistencyAgent",
    "AssetFunctionIOAgent",
    "FunctionalNamingAgent",
    "SymbolComplianceAgent",
    "SignalIntegrityAgent",
    "InterlockAgent",
    "RedundancyAgent",
    "CrossDisciplineAgent",
    "MemoryRegressionAgent",
    "PipelineVersionAgent",
]

GOLDEN_CHECKS = {
    "symbol_external_mm": 12.0,
    "aspect_ratio": 1.0,
    "functional_name_required": True,
    "memory_regression_required": True,
    "orphan_signal_forbidden": True,
    "cmd_run_fault_available_separate": True,
    "document_layout_immutable": True,
    "document_text_only_edit": True,
    "pagination_dynamic": True,
    "datasheet_layout_immutable": True,
}

DOCUMENT_TYPES = ("MD", "ET", "LI", "FD")

DOCUMENT_LAYOUT_POLICY = {
    "template_is_master": True,
    "layout_is_immutable": True,
    "allowed_changes": ["TEXT", "TECHNICAL_VALUES", "TEXTUAL_QUANTITIES", "APPROVED_IMAGES"],
    "forbidden_changes": [
        "MARGINS",
        "TABLE_GEOMETRY",
        "COLUMN_WIDTHS",
        "ROW_HEIGHTS",
        "MERGES",
        "BORDERS",
        "STYLES",
        "FONTS",
        "STRUCTURAL_ALIGNMENT",
        "HEADERS",
        "FOOTERS",
        "LOGO",
        "SIGNATURE",
        "PRINT_AREA",
        "PAGE_ORIENTATION",
        "PAGE_SCALE",
        "SECTION_STRUCTURE",
    ],
    "dynamic_exceptions": ["PAGE_NUMBER", "TOTAL_PAGES", "TOC_PAGE_REFERENCE"],
}

AGENT_CONTRACTS = {
    "DatacenterStructureAgent": {
        "document_template_registry_required": True,
        "preserve_source_template_fingerprint": True,
        "document_types": DOCUMENT_TYPES,
        "layout_policy": "DOCUMENT_LAYOUT_POLICY",
    },
    "DocumentLayoutLockAgent": {
        "block_on_layout_change": True,
        "allow_text_only": True,
        "allow_approved_images": True,
        "allow_dynamic_pagination": True,
    },
    "DataSheetConsistencyAgent": {
        "applies_to": ["FD", "LI"],
        "preserve_internal_layout": True,
        "validate_text_against_reference_drawings": True,
        "validate_tags_codes_quantities": True,
        "pagination_must_match_final_sheet_count": True,
    },
}
