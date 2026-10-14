$ErrorActionPreference = 'Stop'
$AppRoot = if (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'server.py')) {
    $PSScriptRoot
}
else {
    (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
}
$ServerPath = Join-Path $AppRoot 'server.py'
$RuntimeRoot = Join-Path $env:LOCALAPPDATA 'WhiteChronos\SponsoredTokensRuntimes\laya-0.4.6-py311'
$Python = Join-Path $RuntimeRoot 'Scripts\python.exe'
$LayaServe = Join-Path $RuntimeRoot 'Scripts\laya-serve.exe'
$Key = [Environment]::GetEnvironmentVariable('SPONSOREDTOKENS_API_KEY', 'User')

if ([string]::IsNullOrWhiteSpace($Key)) {
    Write-Error 'SPONSOREDTOKENS_API_KEY is not configured for this user.'
    exit 2
}
if (-not (Test-Path -LiteralPath $Python -PathType Leaf) -or
    -not (Test-Path -LiteralPath $LayaServe -PathType Leaf)) {
    Write-Error 'The application-owned Laya runtime is unavailable.'
    exit 3
}

$env:SPONSOREDTOKENS_API_KEY = $Key
$env:LAYA_HOST = '127.0.0.1'
$env:LAYA_PORT = '8770'
$env:LAYA_MODELS = 'multilingual'
$env:LAYA_DEFAULT_MODEL = 'multilingual'
$env:LAYA_PRELOAD = '1'
$env:LAYA_MAX_LOADED = '1'

$ChatProcess = $null
$RouterProcess = $null
$ChatRestartDelay = 1
$RouterRestartDelay = 1
$ChatNextStart = [DateTime]::UtcNow
$RouterNextStart = [DateTime]::UtcNow
$ChatStartedAt = $null
$RouterStartedAt = $null

try {
    while ($true) {
        $now = [DateTime]::UtcNow

        if ($null -ne $RouterProcess -and $RouterProcess.HasExited) {
            if ($null -ne $RouterStartedAt -and ($now - $RouterStartedAt).TotalSeconds -ge 60) {
                $RouterRestartDelay = 1
            }
            $RouterNextStart = $now.AddSeconds($RouterRestartDelay)
            $RouterRestartDelay = [Math]::Min(60, $RouterRestartDelay * 2)
            $RouterProcess = $null
        }
        if ($null -eq $RouterProcess -and $now -ge $RouterNextStart) {
            try {
                $RouterProcess = Start-Process -FilePath $LayaServe -WorkingDirectory $RuntimeRoot -WindowStyle Hidden -PassThru
                $RouterStartedAt = $now
            }
            catch {
                $RouterNextStart = $now.AddSeconds($RouterRestartDelay)
                $RouterRestartDelay = [Math]::Min(60, $RouterRestartDelay * 2)
            }
        }

        if ($null -ne $ChatProcess -and $ChatProcess.HasExited) {
            if ($null -ne $ChatStartedAt -and ($now - $ChatStartedAt).TotalSeconds -ge 60) {
                $ChatRestartDelay = 1
            }
            $ChatNextStart = $now.AddSeconds($ChatRestartDelay)
            $ChatRestartDelay = [Math]::Min(60, $ChatRestartDelay * 2)
            $ChatProcess = $null
        }
        if ($null -eq $ChatProcess -and $now -ge $ChatNextStart) {
            try {
                $ChatProcess = Start-Process -FilePath $Python -ArgumentList @(
                    ('"{0}"' -f $ServerPath), '--port', '8765'
                ) -WorkingDirectory $AppRoot -WindowStyle Hidden -PassThru
                $ChatStartedAt = $now
            }
            catch {
                $ChatNextStart = $now.AddSeconds($ChatRestartDelay)
                $ChatRestartDelay = [Math]::Min(60, $ChatRestartDelay * 2)
            }
        }

        Start-Sleep -Seconds 1
    }
}
finally {
    foreach ($child in @($ChatProcess, $RouterProcess)) {
        if ($null -ne $child -and -not $child.HasExited) {
            Stop-Process -Id $child.Id -Force -ErrorAction SilentlyContinue
        }
    }
}
