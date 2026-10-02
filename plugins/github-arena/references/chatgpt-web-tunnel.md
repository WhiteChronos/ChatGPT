# ChatGPT Web via OpenAI Secure MCP Tunnel

Use this path to connect the local `github_arena` MCP server to ChatGPT Web without exposing a public inbound port.

## Requirements

- Windows with Node.js 18+.
- This repository cloned locally.
- An OpenAI Platform tunnel ID created in Platform tunnel settings.
- A runtime API key available only as the `CONTROL_PLANE_API_KEY` environment variable.
- ChatGPT Developer mode enabled.

Official management page:

`https://platform.openai.com/settings/organization/tunnels`

## Windows setup

Open PowerShell in the repository root.

Set the runtime API key only for the current shell:

```powershell
$env:CONTROL_PLANE_API_KEY = "sk-..."
```

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\plugins\github-arena\scripts\setup_openai_tunnel.ps1 -TunnelId "tunnel_..."
```

The script:

1. detects Windows architecture;
2. downloads the latest official `openai/tunnel-client` release;
3. finds the local GitHub Arena MCP server;
4. creates/updates the `github-arena` tunnel-client profile;
5. runs `tunnel-client doctor --explain`;
6. prints the command needed to keep the tunnel running.

## Start the tunnel

Use the command printed by the installer, equivalent to:

```powershell
tunnel-client run --profile github-arena
```

Keep the process running while ChatGPT uses the plugin.

## Connect from ChatGPT Web

1. Open ChatGPT.
2. Go to Settings → Security and login.
3. Enable Developer mode.
4. Open ChatGPT Plugins.
5. Select the plus button.
6. Under Connection, select **Tunnel**.
7. Select the available tunnel or paste the `tunnel_id`.
8. Create the connection and review the discovered Arena tools.

Expected tools:

- `arena_plan`
- `arena_cards`
- `arena_rubric`
- `arena_review_checklist`

## Scope

Secure MCP Tunnel is appropriate for personal/private use and developer-mode testing. It does not replace a stable public HTTPS MCP endpoint for public plugin submission.

The GitHub connector remains responsible for repository reads/writes. Arena remains read-only and performs review/planning only.
