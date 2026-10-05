# WhiteChronos Capability Registry v2

Registry v2 is an additive capability-contract registry. The existing `registry/integrations` v1 registry remains authoritative for current Runtime Doctor integration routing until a later migration is explicitly designed, implemented, and verified.

The v2 source layout is `registry/capabilities/v2/{contracts,providers,events}`. Contract records, provider-version manifests, and lifecycle-event records are immutable source records once accepted. Lifecycle changes append a new event file; they do not edit a provider `status` field in place.

There is intentionally no manually maintained v2 `index.json`. Discovery is derived deterministically from sorted source-controlled paths, and current lifecycle state is a materialized view reconstructed from append-only events.

Provider manifests reference capability contracts. These records do not introduce direct provider-to-provider implementation dependencies, private database access, shared memory, or runtime invocation. Provider activation, resolution, adapters, knowledge/evolution ledgers, and Zero-Trust runtime enforcement belong to later implementation slices.
