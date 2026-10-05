from __future__ import annotations

from dataclasses import dataclass

from .capability_model import validate_capability_id, validate_provider_id, validate_semver


@dataclass(frozen=True)
class ErrorMapping:
    source_error: str
    target_error: str

    def __post_init__(self) -> None:
        if not self.source_error or not self.target_error:
            raise ValueError("error mapping values must be non-empty")


@dataclass(frozen=True)
class CapabilityAdapter:
    adapter_id: str
    version: str
    implementation_provider_id: str
    implementation_version: str
    source_contract_id: str
    source_version: str
    target_contract_id: str
    target_version: str
    transformation: str
    lossiness: str
    information_loss: tuple[str, ...]
    unsupported_cases: tuple[str, ...]
    error_mapping: tuple[ErrorMapping, ...]
    conformance_tests: tuple[str, ...]
    extensions: dict[str, object]

    def __post_init__(self) -> None:
        validate_provider_id(self.adapter_id)
        validate_semver(self.version, label="adapter version")
        validate_provider_id(self.implementation_provider_id)
        validate_semver(self.implementation_version, label="implementation_version")
        validate_capability_id(self.source_contract_id)
        validate_semver(self.source_version, label="source_version")
        validate_capability_id(self.target_contract_id)
        validate_semver(self.target_version, label="target_version")
        if not self.transformation:
            raise ValueError("transformation must be non-empty")
        if self.lossiness not in {"LOSSLESS", "LOSSY"}:
            raise ValueError(f"invalid lossiness: {self.lossiness!r}")
        if self.lossiness == "LOSSLESS" and self.information_loss:
            raise ValueError("LOSSLESS adapter cannot declare information loss")
        if self.lossiness == "LOSSY" and not self.information_loss:
            raise ValueError("LOSSY adapter must declare information loss")
        if (self.source_contract_id, self.source_version) == (self.target_contract_id, self.target_version):
            raise ValueError("adapter exact self-loop is not allowed")
        if any(not value for value in self.information_loss):
            raise ValueError("information_loss entries must be non-empty")
        if any(not value for value in self.unsupported_cases):
            raise ValueError("unsupported_cases entries must be non-empty")
        if any(not value for value in self.conformance_tests):
            raise ValueError("conformance_tests entries must be non-empty")

    @property
    def key(self) -> tuple[str, str]:
        return (self.adapter_id, self.version)

    @property
    def source_key(self) -> tuple[str, str]:
        return (self.source_contract_id, self.source_version)

    @property
    def target_key(self) -> tuple[str, str]:
        return (self.target_contract_id, self.target_version)

    @property
    def is_lossy(self) -> bool:
        return self.lossiness == "LOSSY"
