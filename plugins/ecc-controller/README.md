# ECC Controller

WhiteChronos integration layer for the official [affaan-m/ECC] upstream.

## Runtime strategy

- **Official ECC Codex plugin**: primary ECC runtime and source of behavioral skills.
- **ECC Controller**: WhiteChronos routing, provenance, safety, and fallback layer.
- **Read-only mirror**: full upstream snapshot for audit, recovery, and comparison.
- **Superpowers**: remains the default software-development process layer.
- **Matt Pocock skills**: complementary specialist workflows.
- **GitHub Arena**: final adversarial review for high-impact work.

This repository does not maintain a behavioral fork of ECC.

## Upstream snapshot

- Repository: `affaan-m/ECC`
- Version observed: `2.2.3`
- Commit observed: `ef648e01899ba3e8dc6371642deaaf64b4477775`
- License: MIT
- Observed canonical surfaces: 293 Skills, 68 agents, 94 command shims
- Native Codex plugin: yes

See `upstream.lock.json`.

## Codex

The WhiteChronos marketplace points its `ecc` entry directly at the official upstream Git repository and enables it for trusted Codex sessions. The local `ecc-controller` plugin adds routing and governance only; it does not duplicate ECC hooks or MCP servers.

ECC's native Codex hook and MCP declarations remain owned by the official plugin.

## Mirror

`vendor/affaan-m-ecc/` is a read-only byte mirror maintained by `.github/workflows/sync-ecc-mirror.yml`.

Synchronization:

1. clones the official upstream without running upstream code;
2. replaces the mirror bytes;
3. strips only the nested `.git` metadata;
4. records commit/version and catalog counts;
5. pushes a review branch when upstream changes;
6. attempts to open a PR, but tolerates repository policy that blocks Actions-created PRs.

Never execute code merely because it exists in the mirror.
