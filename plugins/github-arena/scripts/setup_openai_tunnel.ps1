param(
  [Parameter(Mandatory = $true)]
  [string]$TunnelId,
  [string]$RepoPath = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path,
  [string]$Profile = "github-arena"
)

$ErrorActionPreference = "Stop"

if (-not $env:CONTROL_PLANE_API_KEY) {
  throw "Defina CONTROL_PLANE_API_KEY no PowerShell antes de executar este script."
}

$arch = if ($env:PROCESSOR_ARCHITECTURE -eq "ARM64") { "arm64" } else { "amd64" }
$baseDir = Join-Path $env:LOCALAPPDATA "WhiteChronos\GitHubArena\tunnel-client"
New-Item -ItemType Directory -Force -Path $baseDir | Out-Null

$release = Invoke-RestMethod -Uri "https://api.github.com/repos/openai/tunnel-client/releases/latest" -Headers @{ "User-Agent" = "github-arena-tunnel-installer" }
$pattern = "^tunnel-client-v.*-windows-$arch\.zip$"
$asset = $release.assets | Where-Object { $_.name -match $pattern } | Select-Object -First 1

if (-not $asset) {
  throw "Nao encontrei o binario tunnel-client para Windows/$arch na release mais recente."
}

$zipPath = Join-Path $baseDir $asset.name
Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zipPath

$extractDir = Join-Path $baseDir "current"
if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force }
Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force

$client = Get-ChildItem -Path $extractDir -Recurse -Filter "tunnel-client.exe" | Select-Object -First 1
if (-not $client) {
  throw "tunnel-client.exe nao foi encontrado apos extrair o pacote."
}

$mcpServer = Join-Path $RepoPath "plugins\github-arena\mcp-server\mcp_server.mjs"
if (-not (Test-Path $mcpServer)) {
  throw "Servidor MCP nao encontrado em: $mcpServer"
}

$node = (Get-Command node -ErrorAction Stop).Source
$mcpCommand = '"' + $node + '" "' + $mcpServer + '"'

Write-Host "Configurando perfil '$Profile' para tunnel $TunnelId"
& $client.FullName init --sample sample_mcp_stdio_local --profile $Profile --tunnel-id $TunnelId --mcp-command $mcpCommand

Write-Host "Executando diagnostico..."
& $client.FullName doctor --profile $Profile --explain

Write-Host ""
Write-Host "Configuracao concluida."
Write-Host "Para manter o ChatGPT conectado, execute:"
Write-Host ('& "' + $client.FullName + '" run --profile ' + $Profile)
Write-Host ""
Write-Host "Depois, no ChatGPT: Plugins > + > Connection: Tunnel > selecione ou informe o tunnel_id."
