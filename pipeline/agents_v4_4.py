# Referência versionada do pipeline de agentes v4.4
# Implementação operacional mantida no pacote local AUTOMAÇÃO_Governanca_Engenharia_v4_4.

AGENTS = [
    "DatacenterStructureAgent",
    "DocumentUnderstandingAgent",
    "EvidenceTraceabilityAgent",
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
}
