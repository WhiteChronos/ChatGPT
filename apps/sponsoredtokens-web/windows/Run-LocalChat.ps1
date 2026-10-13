$ErrorActionPreference = 'Stop'
$AppRoot = if (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'server.py')) {
    $PSScriptRoot
}
else {
    (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
}
$ServerPath = Join-Path $AppRoot 'server.py'
$Key = [Environment]::GetEnvironmentVariable('SPONSOREDTOKENS_API_KEY', 'User')
$JevKey = [Environment]::GetEnvironmentVariable('TYPESAFE_API_KEY', 'User')

if ([string]::IsNullOrWhiteSpace($Key)) {
    Write-Error 'SPONSOREDTOKENS_API_KEY is not configured for this user.'
    exit 2
}

$env:SPONSOREDTOKENS_API_KEY = $Key
if (-not [string]::IsNullOrWhiteSpace($JevKey)) {
    $env:TYPESAFE_API_KEY = $JevKey
}
$Python = (Get-Command python -ErrorAction Stop).Source
while ($true) {
    & $Python $ServerPath --port 8765
    Start-Sleep -Seconds 5
}
