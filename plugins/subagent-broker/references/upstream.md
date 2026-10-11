# Upstream provenance

Canonical upstream ecosystem: https://github.com/Shubhamsaboo/awesome-llm-apps.git

- ref: `main`
- pinned commit: `4bf51ab704fb2c5b3803cd5191b30d7dcdb51dc2`
- license at the pinned repository root: Apache-2.0
- relationship: agent ecosystem reference for the WhiteChronos Subagent Broker

The upstream repository is independently maintained and contains a catalog of
agent applications, examples, and skills. It does not directly provide the
`subagent_broker` MCP server contract used by WhiteChronos. The executable MCP
adapter remains local at `plugins/subagent-broker` so the runtime manifest and
the eight Broker lifecycle tools continue to resolve from the primary repository.

Re-check provenance, licensing, and security before importing substantive source
from the upstream repository. External projects linked by that catalog require
their own review and do not inherit the root repository license automatically.
