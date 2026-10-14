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
$RouterUrl = 'http://127.0.0.1:8770/'
$LayaRequirement = 'laya[serve]==0.4.6'
$SourceRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$RequirementsPath = Join-Path $SourceRoot 'requirements-laya.txt'
$WhiteChronosRoot = Join-Path $env:LOCALAPPDATA 'WhiteChronos'
$InstallRoot = Join-Path $WhiteChronosRoot 'SponsoredTokensLocalChat'
$RuntimeBaseRoot = Join-Path $WhiteChronosRoot 'SponsoredTokensRuntimes'
$RuntimeRoot = Join-Path $RuntimeBaseRoot 'laya-0.4.6-py311'
$RuntimePython = Join-Path $RuntimeRoot 'Scripts\python.exe'
$RunnerPath = Join-Path $InstallRoot 'Run-LocalChat.ps1'
$StartupShortcut = Join-Path ([Environment]::GetFolderPath('Startup')) ($TaskName + '.lnk')

function Write-Result([System.Collections.IDictionary]$Value) {
    if ($Json) { $Value | ConvertTo-Json -Compress }
    else { $Value.GetEnumerator() | ForEach-Object { '{0}={1}' -f $_.Key, $_.Value } }
}

function Test-PathWithinRoot([string]$Path, [string]$Root) {
    $candidate = [IO.Path]::GetFullPath($Path).TrimEnd('\', '/')
    $parent = [IO.Path]::GetFullPath($Root).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    return $candidate.StartsWith($parent, [System.StringComparison]::OrdinalIgnoreCase)
}

function Assert-ContainedPath([string]$Path, [string]$Root) {
    if (-not (Test-PathWithinRoot -Path $Path -Root $Root)) {
        throw 'Refusing an operation outside the approved WhiteChronos directory.'
    }
}

function Remove-ContainedPath([string]$Path, [string]$Root) {
    Assert-ContainedPath -Path $Path -Root $Root
    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
}

function Get-ChatHealth {
    try {
        $health = Invoke-RestMethod -Uri ($LocalUrl + 'api/health') -TimeoutSec 2
        $router = if ($health.router -eq 'laya') { 'laya' } else { 'deterministic' }
        return [pscustomobject]@{
            running = $true
            ready = [bool]$health.ready
            routerReady = [bool]$health.router_ready
            router = $router
        }
    }
    catch {
        return [pscustomobject]@{
            running = $false
            ready = $false
            routerReady = $false
            router = 'deterministic'
        }
    }
}

function Get-RouterHealth {
    try {
        $null = Invoke-RestMethod -Uri ($RouterUrl + 'health') -TimeoutSec 2
        return [pscustomobject]@{ running = $true; ready = $true }
    }
    catch {
        return [pscustomobject]@{ running = $false; ready = $false }
    }
}

function Get-LocalChatState {
    $chat = Get-ChatHealth
    $router = Get-RouterHealth
    [ordered]@{
        installed = (
            (Test-Path -LiteralPath $StartupShortcut -PathType Leaf) -and
            (Test-Path -LiteralPath $RunnerPath -PathType Leaf) -and
            (Test-Path -LiteralPath $RuntimePython -PathType Leaf)
        )
        running = $chat.running
        ready = $chat.ready
        routerRunning = $router.running
        routerReady = ($router.ready -and $chat.routerReady)
        router = $chat.router
        url = $LocalUrl
        task = $TaskName
    }
}

function Get-InstalledProcesses {
    $runnerFullPath = [IO.Path]::GetFullPath($RunnerPath)
    $installedServerFullPath = [IO.Path]::GetFullPath((Join-Path $InstallRoot 'server.py'))
    @(Get-CimInstance Win32_Process | Where-Object {
        if ($_.ProcessId -eq $PID) { return $false }
        $name = [string]$_.Name
        $commandLine = [string]$_.CommandLine
        $executable = [string]$_.ExecutablePath
        $isSupervisor = (
            $name -in @('pwsh.exe', 'powershell.exe') -and
            $commandLine.IndexOf($runnerFullPath, [System.StringComparison]::OrdinalIgnoreCase) -ge 0
        )
        $isRuntimeChild = (
            $name -in @('python.exe', 'pythonw.exe', 'laya-serve.exe') -and
            -not [string]::IsNullOrWhiteSpace($executable) -and
            (Test-PathWithinRoot -Path $executable -Root $RuntimeRoot)
        )
        $isInstalledChat = (
            $name -in @('python.exe', 'pythonw.exe') -and
            $commandLine.IndexOf($installedServerFullPath, [System.StringComparison]::OrdinalIgnoreCase) -ge 0
        )
        $isSupervisor -or $isRuntimeChild -or $isInstalledChat
    })
}

function Stop-InstalledProcesses {
    $processes = @(Get-InstalledProcesses)
    foreach ($process in ($processes | Sort-Object { if ($_.Name -match 'powershell|pwsh') { 0 } else { 1 } })) {
        Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
    }
}

function Test-LayaRuntime([string]$PythonPath) {
    if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
        return $false
    }
    & $PythonPath -c 'import importlib.metadata as m, laya.serve, sys;sys.exit(0 if m.version("laya")=="0.4.6" else 1)'
    return $LASTEXITCODE -eq 0
}

function Get-Python311Launcher {
    $py = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($py) {
        & $py.Source -3.11 -c 'import sys;raise SystemExit(0 if sys.version_info[:2]==(3,11) else 1)'
        if ($LASTEXITCODE -eq 0) {
            return [pscustomobject]@{ FilePath = $py.Source; Prefix = @('-3.11') }
        }
    }
    $python = Get-Command python.exe -ErrorAction Stop
    & $python.Source -c 'import sys;raise SystemExit(0 if sys.version_info[:2]==(3,11) else 1)'
    if ($LASTEXITCODE -ne 0) {
        throw 'Python 3.11 is required for the isolated Laya runtime.'
    }
    return [pscustomobject]@{ FilePath = $python.Source; Prefix = @() }
}

function Prepare-LayaRuntime {
    if (Test-LayaRuntime -PythonPath $RuntimePython) {
        return [pscustomobject]@{ Path = $RuntimeRoot; Activate = $false }
    }
    if (-not (Test-Path -LiteralPath $RequirementsPath -PathType Leaf)) {
        throw 'The reviewed Laya requirement file is missing.'
    }
    New-Item -ItemType Directory -Path $RuntimeBaseRoot -Force | Out-Null
    $stage = Join-Path $RuntimeBaseRoot ('laya-0.4.6-py311.prepare-' + [Guid]::NewGuid().ToString('N'))
    Assert-ContainedPath -Path $stage -Root $RuntimeBaseRoot
    try {
        $launcher = Get-Python311Launcher
        $venvArguments = @($launcher.Prefix) + @('-m', 'venv', $stage)
        & $launcher.FilePath @venvArguments
        if ($LASTEXITCODE -ne 0) { throw 'Python runtime preparation failed.' }
        $stagePython = Join-Path $stage 'Scripts\python.exe'
        & $stagePython -m pip install --disable-pip-version-check --requirement $RequirementsPath
        if ($LASTEXITCODE -ne 0) { throw 'Laya dependency preparation failed.' }
        if (-not (Test-LayaRuntime -PythonPath $stagePython)) {
            throw 'Laya runtime verification failed.'
        }
        return [pscustomobject]@{ Path = $stage; Activate = $true }
    }
    catch {
        Remove-ContainedPath -Path $stage -Root $RuntimeBaseRoot
        throw 'Laya runtime preparation failed safely.'
    }
}

function Stage-Application {
    $stage = Join-Path $WhiteChronosRoot ('SponsoredTokensLocalChat.prepare-' + [Guid]::NewGuid().ToString('N'))
    Assert-ContainedPath -Path $stage -Root $WhiteChronosRoot
    $staticRoot = Join-Path $stage 'static'
    New-Item -ItemType Directory -Path $staticRoot -Force | Out-Null
    foreach ($name in @('providers.py', 'routing.py', 'server.py')) {
        Copy-Item -LiteralPath (Join-Path $SourceRoot $name) -Destination $stage -Force
    }
    foreach ($name in @('index.html', 'app.css', 'app.js')) {
        Copy-Item -LiteralPath (Join-Path (Join-Path $SourceRoot 'static') $name) -Destination $staticRoot -Force
    }
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'Run-LocalChat.ps1') -Destination $stage -Force
    return $stage
}

function Restore-InstalledApplication([string]$BackupPath) {
    Assert-ContainedPath -Path $InstallRoot -Root $WhiteChronosRoot
    if (Test-Path -LiteralPath $InstallRoot) {
        Remove-ContainedPath -Path $InstallRoot -Root $WhiteChronosRoot
    }
    if (Test-Path -LiteralPath $BackupPath) {
        Move-Item -LiteralPath $BackupPath -Destination $InstallRoot
    }
}

function Set-StartupShortcut {
    $shellPath = (Get-Command powershell.exe -ErrorAction Stop).Source
    $arguments = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "{0}"' -f $RunnerPath
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($StartupShortcut)
    $shortcut.TargetPath = $shellPath
    $shortcut.Arguments = $arguments
    $shortcut.WorkingDirectory = $InstallRoot
    $shortcut.WindowStyle = 7
    $shortcut.Description = 'Starts the private SponsoredTokens chat and local Laya router.'
    $shortcut.Save()
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
        runtimeRoot = $RuntimeRoot
        layaRequirement = $LayaRequirement
        routerUrl = $RouterUrl
        phases = @('prepare-runtime', 'stage-application', 'stop-installed', 'activate', 'shortcut')
    })
    exit 0
}

$changed = $false
switch ($Action) {
    'Install' {
        if ($PSCmdlet.ShouldProcess($TaskName, 'Install the local chat and isolated Laya runtime')) {
            $preparedRuntime = Prepare-LayaRuntime
            $applicationStage = Stage-Application
            Stop-InstalledProcesses

            $applicationBackup = $InstallRoot + '.backup'
            $runtimeBackup = $RuntimeRoot + '.backup'
            Assert-ContainedPath -Path $InstallRoot -Root $WhiteChronosRoot
            Assert-ContainedPath -Path $RuntimeRoot -Root $WhiteChronosRoot
            try {
                if ($preparedRuntime.Activate) {
                    if (Test-Path -LiteralPath $runtimeBackup) {
                        Remove-ContainedPath -Path $runtimeBackup -Root $RuntimeBaseRoot
                    }
                    if (Test-Path -LiteralPath $RuntimeRoot) {
                        Move-Item -LiteralPath $RuntimeRoot -Destination $runtimeBackup
                    }
                    Move-Item -LiteralPath $preparedRuntime.Path -Destination $RuntimeRoot
                }

                if (Test-Path -LiteralPath $applicationBackup) {
                    Remove-ContainedPath -Path $applicationBackup -Root $WhiteChronosRoot
                }
                if (Test-Path -LiteralPath $InstallRoot) {
                    Move-Item -LiteralPath $InstallRoot -Destination $applicationBackup
                }
                Move-Item -LiteralPath $applicationStage -Destination $InstallRoot
                Set-StartupShortcut

                $legacyTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
                if ($legacyTask) {
                    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
                    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
                }
                $changed = $true
            }
            catch {
                Restore-InstalledApplication -BackupPath $applicationBackup
                if ($preparedRuntime.Activate -and (Test-Path -LiteralPath $runtimeBackup)) {
                    if (Test-Path -LiteralPath $RuntimeRoot) {
                        Remove-ContainedPath -Path $RuntimeRoot -Root $RuntimeBaseRoot
                    }
                    Move-Item -LiteralPath $runtimeBackup -Destination $RuntimeRoot
                }
                throw 'Installation activation failed; the previous application was restored.'
            }
        }
    }
    'Start' {
        $state = Get-LocalChatState
        if (-not $state.installed) { throw 'Automatic start is not installed.' }
        $supervisors = @(Get-InstalledProcesses | Where-Object { $_.Name -in @('pwsh.exe', 'powershell.exe') })
        if ($supervisors.Count -eq 0 -and $PSCmdlet.ShouldProcess($TaskName, 'Start local chat supervisor')) {
            $shellPath = (Get-Command powershell.exe -ErrorAction Stop).Source
            Start-Process -FilePath $shellPath -ArgumentList @(
                '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
                '-File', ('"{0}"' -f $RunnerPath)
            ) -WorkingDirectory $InstallRoot -WindowStyle Hidden
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
        Assert-ContainedPath -Path $InstallRoot -Root $WhiteChronosRoot
        Assert-ContainedPath -Path $RuntimeRoot -Root $WhiteChronosRoot
        if ($PSCmdlet.ShouldProcess($TaskName, 'Remove automatic start and application-owned runtime')) {
            Stop-InstalledProcesses
            if (Test-Path -LiteralPath $StartupShortcut) {
                Remove-Item -LiteralPath $StartupShortcut -Force
            }
            Remove-ContainedPath -Path $InstallRoot -Root $WhiteChronosRoot
            Remove-ContainedPath -Path $RuntimeRoot -Root $RuntimeBaseRoot
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
