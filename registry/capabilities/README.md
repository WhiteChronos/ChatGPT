# WhiteChronos Capability Registry v2

Registry v2 is an additive capability-contract registry. The existing `registry/integrations` v1 registry remains authoritative for current Runtime Doctor integration routing until a later migration is explicitly designed, implemented, and verified.

The v2 source layout is `registry/capabilities/v2/{contracts,providers,events}`. Contract records, provider-version manifests, and lifecycle-event records are immutable source records once accepted. Lifecycle changes append a new event file; they do not edit a provider `status` field in place.

There is intentionally no manually maintained v2 `index.json`. Discovery is derived deterministically from sorted source-controlled paths, and current lifecycle state is a materialized view reconstructed from append-only events.

Provider manifests reference capability contracts. These records do not introduce direct provider-to-provider implementation dependencies, private database access, shared memory, or runtime invocation. Provider activation, resolution, adapters, knowledge/evolution ledgers, and Zero-Trust runtime enforcement belong to later implementation slices.

## Adapters

Phase 2 adds immutable Adapter records under `registry/capabilities/v2/adapters/`. An Adapter names an exact source contract/version and exact target contract/version, while provenance and lifecycle belong to its exact implementation provider (`implementation_provider_id`, `implementation_version`). Adapter records are append-only accepted state just like contracts, provider manifests, and lifecycle events.

Adapters describe semantic bridges only. They do not invoke providers, grant authorization, or bypass provider isolation. Runtime execution, authorization, health routing, and Zero-Trust enforcement remain separate later phases.

Local placement never grants permission for one provider to import or read another provider's private implementation. Cross-provider interaction is contract-based.

The CI boundary gate is `python pipeline/capability_dependency_policy.py --repo .`; it derives local provider roots only from accepted Registry v2 manifests and fails closed on ambiguous roots.

