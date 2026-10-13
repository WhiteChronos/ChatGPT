[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Install', 'Start', 'Status', 'Stop', 'Uninstall')]
    [string]$Action,
    [switch]$Json
)

$ErrorActionPreference = 'Stop'
$TaskName = 'WhiteChronos-SponsoredTokens-LocalChat'
$LocalUrl = 'http://127.0.0.1:8765/'
$SourceRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$InstallRoot = Join-Path $env:LOCALAPPDATA 'WhiteChronos\SponsoredTokensLocalChat'
$RunnerPath = Join-Path $InstallRoot 'Run-LocalChat.ps1'
$StartupShortcut = Join-Path ([Environment]::GetFolderPath('Startup')) ($TaskName + '.lnk')

function Write-Result([System.Collections.IDictionary]$Value) {
    if ($Json) { $Value | ConvertTo-Json -Compress }
    else { $Value.GetEnumerator() | ForEach-Object { '{0}={1}' -f $_.Key, $_.Value } }
}

function Get-Health {
    try {
        $health = Invoke-RestMethod -Uri ($LocalUrl + 'api/health') -TimeoutSec 2
        return [pscustomobject]@{ running = $true; ready = [bool]$health.ready }
    }
    catch {
        return [pscustomobject]@{ running = $false; ready = $false }
    }
}

function Get-LocalChatState {
    $health = Get-Health
    [ordered]@{
        installed = Test-Path -LiteralPath $StartupShortcut -PathType Leaf
        running = $health.running
        ready = $health.ready
        url = $LocalUrl
        task = $TaskName
    }
}

function Stop-InstalledProcesses {
    if (-not (Test-Path -LiteralPath $InstallRoot)) { return }
    $processes = @(Get-CimInstance Win32_Process | Where-Object {
        $_.ProcessId -ne $PID -and $_.CommandLine -and
        $_.CommandLine.Contains($InstallRoot, [System.StringComparison]::OrdinalIgnoreCase) -and
        $_.Name -in @('pwsh.exe', 'powershell.exe', 'python.exe', 'pythonw.exe')
    })
    foreach ($process in ($processes | Sort-Object { if ($_.Name -match 'powershell|pwsh') { 0 } else { 1 } })) {
        Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
    }
}

if ($Action -eq 'Status') {
    Write-Result (Get-LocalChatState)
    exit 0
}

if ($Action -eq 'Install' -and $WhatIfPreference) {
    Write-Result ([ordered]@{
        action = 'Install'
        changed = $false
        task = $TaskName
        url = $LocalUrl
        keySource = 'SPONSOREDTOKENS_API_KEY'
        installRoot = $InstallRoot
    })
    exit 0
}

$changed = $false
switch ($Action) {
    'Install' {
        $sourceRunner = Join-Path $PSScriptRoot 'Run-LocalChat.ps1'
        if (-not (Test-Path -LiteralPath $sourceRunner -PathType Leaf)) {
            throw 'The local chat runner is missing.'
        }
        if ($PSCmdlet.ShouldProcess($TaskName, 'Install automatic start for the current user')) {
            Stop-InstalledProcesses
            $staticRoot = Join-Path $InstallRoot 'static'
            New-Item -ItemType Directory -Path $staticRoot -Force | Out-Null
            foreach ($name in @('providers.py', 'routing.py', 'server.py')) {
                Copy-Item -LiteralPath (Join-Path $SourceRoot $name) -Destination $InstallRoot -Force
            }
            foreach ($name in @('index.html', 'app.css', 'app.js')) {
                Copy-Item -LiteralPath (Join-Path (Join-Path $SourceRoot 'static') $name) -Destination $staticRoot -Force
            }
            Copy-Item -LiteralPath $sourceRunner -Destination $RunnerPath -Force

            # Remove the exact legacy task from earlier versions of this installer.
            $legacyTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
            if ($legacyTask) {
                Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
                Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            }

            $shellPath = (Get-Command powershell.exe -ErrorAction Stop).Source
            $arguments = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "{0}"' -f $RunnerPath
            $shell = New-Object -ComObject WScript.Shell
            $shortcut = $shell.CreateShortcut($StartupShortcut)
            $shortcut.TargetPath = $shellPath
            $shortcut.Arguments = $arguments
            $shortcut.WorkingDirectory = $InstallRoot
            $shortcut.WindowStyle = 7
            $shortcut.Description = 'Starts the private SponsoredTokens loopback chat.'
            $shortcut.Save()
            $changed = $true
        }
    }
    'Start' {
        if (-not (Test-Path -LiteralPath $StartupShortcut -PathType Leaf)) {
            throw 'Automatic start is not installed.'
        }
        if (-not (Get-Health).running -and $PSCmdlet.ShouldProcess($TaskName, 'Start local chat supervisor')) {
            $shellPath = (Get-Command powershell.exe -ErrorAction Stop).Source
            $arguments = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "{0}"' -f $RunnerPath
            Start-Process -FilePath $shellPath -ArgumentList $arguments -WorkingDirectory $InstallRoot -WindowStyle Hidden
            $changed = $true
        }
    }
    'Stop' {
        if ($PSCmdlet.ShouldProcess($TaskName, 'Stop installed local chat processes')) {
            Stop-InstalledProcesses
            $changed = $true
        }
    }
    'Uninstall' {
        if ($PSCmdlet.ShouldProcess($TaskName, 'Remove automatic start')) {
            Stop-InstalledProcesses
            if (Test-Path -LiteralPath $StartupShortcut) {
                Remove-Item -LiteralPath $StartupShortcut -Force
            }
            if (Test-Path -LiteralPath $InstallRoot) {
                $resolvedInstallRoot = (Resolve-Path -LiteralPath $InstallRoot).Path
                $expectedParent = Join-Path $env:LOCALAPPDATA 'WhiteChronos'
                if (-not $resolvedInstallRoot.StartsWith($expectedParent, [System.StringComparison]::OrdinalIgnoreCase)) {
                    throw 'Refusing to remove files outside the expected installation directory.'
                }
                Remove-Item -LiteralPath $resolvedInstallRoot -Recurse -Force
            }
            $changed = $true
        }
    }
}

Write-Result ([ordered]@{
    action = $Action
    changed = $changed
    task = $TaskName
    url = $LocalUrl
})
