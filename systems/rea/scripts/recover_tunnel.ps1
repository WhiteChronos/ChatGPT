param(
    [string]$Alias = "rea-privado",
    [string]$TunnelClient = "tunnel-client",
    [string]$TunnelId = $env:CONTROL_PLANE_TUNNEL_ID,
    [string]$CodeRoot = $env:REA_CODE_ROOT,
    [string]$Python = $env:REA_PYTHON
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Persistent path: tunnel-client runtimes connect ...
# Verification: tunnel-client runtimes status <alias> --json

if (-not $env:CONTROL_PLANE_API_KEY) {
    throw "CONTROL_PLANE_API_KEY is required in the local environment. Do not pass the literal key on the command line."
}
if (-not $TunnelId) { throw "CONTROL_PLANE_TUNNEL_ID is required." }
if (-not $CodeRoot) { throw "REA_CODE_ROOT must point to the explicitly authorized source-code root." }

$client = Get-Command $TunnelClient -ErrorAction Stop
$clientPath = $client.Source
$reaRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$serverPath = (Resolve-Path (Join-Path $reaRoot "src\sdk_server.py")).Path
$authorizedRoot = (Resolve-Path $CodeRoot).Path
if (-not $Python) { $Python = "python" }
$pythonCmd = Get-Command $Python -ErrorAction Stop
$pythonPath = $pythonCmd.Source

& $clientPath runtimes --help *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Installed tunnel-client does not expose 'runtimes'. Install the current supported release before continuing."
}

function Get-ReaTunnelStatus {
    $raw = & $clientPath runtimes status $Alias --json 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $raw) { return $null }
    try { return ($raw | Out-String | ConvertFrom-Json) } catch { return $null }
}

$existing = Get-ReaTunnelStatus
if ($existing -and $existing.process_running -eq $true -and $existing.healthy -eq $true -and $existing.ready -eq $true) {
    $existing | ConvertTo-Json -Depth 8
    exit 0
}

$mcpCommand = '"' + $pythonPath + '" "' + $serverPath + '" --root "' + $authorizedRoot + '" --transport stdio'
$connectArgs = @(
    "runtimes", "connect",
    "--alias", $Alias,
    "--tunnel-id", $TunnelId,
    "--runtime-api-key", "env:CONTROL_PLANE_API_KEY",
    "--mcp-command", $mcpCommand,
    "--json"
)
$null = & $clientPath @connectArgs
if ($LASTEXITCODE -ne 0) {
    throw "tunnel-client runtimes connect failed. Run tunnel-client doctor/diagnostics on the host and inspect local diagnostics without exposing secrets."
}

$status = Get-ReaTunnelStatus
if (-not $status) { throw "Managed runtime was launched but status could not be read." }
if ($status.process_running -ne $true -or $status.healthy -ne $true -or $status.ready -ne $true) {
    $safe = $status | ConvertTo-Json -Depth 8
    throw "Managed REA tunnel is not fully ready. Status: $safe"
}
$status | ConvertTo-Json -Depth 8
