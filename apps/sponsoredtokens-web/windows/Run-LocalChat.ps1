$ErrorActionPreference = 'Stop'
$AppRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$ServerPath = Join-Path $AppRoot 'server.py'
$Key = [Environment]::GetEnvironmentVariable('SPONSOREDTOKENS_API_KEY', 'User')

if ([string]::IsNullOrWhiteSpace($Key)) {
    Write-Error 'SPONSOREDTOKENS_API_KEY is not configured for this user.'
    exit 2
}

$env:SPONSOREDTOKENS_API_KEY = $Key
$Python = (Get-Command python -ErrorAction Stop).Source
& $Python $ServerPath --port 8765
exit $LASTEXITCODE
