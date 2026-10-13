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
$RunnerPath = Join-Path $PSScriptRoot 'Run-LocalChat.ps1'

function Write-Result([System.Collections.IDictionary]$Value) {
    if ($Json) {
        $Value | ConvertTo-Json -Compress
    }
    else {
        $Value.GetEnumerator() | ForEach-Object { '{0}={1}' -f $_.Key, $_.Value }
    }
}

function Get-LocalChatState {
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    $ready = $false
    $running = $false
    try {
        $health = Invoke-RestMethod -Uri ($LocalUrl + 'api/health') -TimeoutSec 2
        $running = $true
        $ready = [bool]$health.ready
    }
    catch {
        $running = $false
        $ready = $false
    }
    [ordered]@{
        installed = [bool]$task
        running = $running
        ready = $ready
        url = $LocalUrl
        task = $TaskName
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
    })
    exit 0
}

$changed = $false
switch ($Action) {
    'Install' {
        if (-not (Test-Path -LiteralPath $RunnerPath -PathType Leaf)) {
            throw 'The local chat runner is missing.'
        }
        if ($PSCmdlet.ShouldProcess($TaskName, 'Register automatic start at user logon')) {
            $shellPath = (Get-Process -Id $PID).Path
            $arguments = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "{0}"' -f $RunnerPath
            $taskAction = New-ScheduledTaskAction -Execute $shellPath -Argument $arguments
            $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
            $trigger = New-ScheduledTaskTrigger -AtLogOn -User $currentUser
            $settings = New-ScheduledTaskSettingsSet `
                -StartWhenAvailable `
                -RestartCount 20 `
                -RestartInterval (New-TimeSpan -Minutes 1) `
                -ExecutionTimeLimit ([TimeSpan]::Zero) `
                -MultipleInstances IgnoreNew
            $principal = New-ScheduledTaskPrincipal `
                -UserId $currentUser `
                -LogonType Interactive `
                -RunLevel Limited
            Register-ScheduledTask `
                -TaskName $TaskName `
                -Action $taskAction `
                -Trigger $trigger `
                -Settings $settings `
                -Principal $principal `
                -Description 'Starts the private SponsoredTokens loopback chat.' `
                -Force | Out-Null
            $changed = $true
        }
    }
    'Start' {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if (-not $task) { throw 'Automatic start is not installed.' }
        if ($PSCmdlet.ShouldProcess($TaskName, 'Start local chat task')) {
            Start-ScheduledTask -TaskName $TaskName
            $changed = $true
        }
    }
    'Stop' {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task -and $PSCmdlet.ShouldProcess($TaskName, 'Stop local chat task')) {
            Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
            $changed = $true
        }
    }
    'Uninstall' {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task -and $PSCmdlet.ShouldProcess($TaskName, 'Remove automatic start task')) {
            Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
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
