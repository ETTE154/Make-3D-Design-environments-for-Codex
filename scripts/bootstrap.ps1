#requires -Version 5.1
<#
Plan-only by default. Run with -Apply for installation.
No upgrades, no global configuration changes, no administrator-shell requirement.
Windows scripts have not been executed on the author's Linux validation host.
#>
[CmdletBinding()]
param(
    [switch]$Apply,
    [switch]$AcceptAgreements,
    [switch]$SkipEditor
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Run on the actual native Windows CAD workstation.' }
$Root = Split-Path -Parent $PSScriptRoot
$ReportDir = Join-Path $Root ('.local\bootstrap-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null
$Records = New-Object System.Collections.Generic.List[object]

function Invoke-Captured([string]$Executable, [string[]]$Arguments) {
    $old = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $lines = @(& $Executable @Arguments 2>&1)
        $code = $LASTEXITCODE
        $text = ($lines | ForEach-Object { $_.ToString() }) -join "`n"
        return [pscustomobject]@{ Code=$code; Text=$text }
    } finally { $ErrorActionPreference = $old }
}

function Find-Tool([string]$Name) {
    $c = Get-Command $Name -ErrorAction SilentlyContinue
    if ($c) { return $c.Source }
    return $null
}
function Find-Git {
    $p = Find-Tool 'git.exe'; if ($p) { return $p }
    foreach ($b in @($env:ProgramFiles, $env:LOCALAPPDATA)) {
        if ($b) { $p = Join-Path $b 'Git\cmd\git.exe'; if (Test-Path $p) { return $p } }
    }
    return $null
}
function Find-Code {
    $p = Find-Tool 'code.cmd'; if ($p) { return $p }
    foreach ($b in @($env:LOCALAPPDATA, $env:ProgramFiles)) {
        if ($b) {
            foreach ($s in @('Programs\Microsoft VS Code\bin\code.cmd', 'Microsoft VS Code\bin\code.cmd')) {
                $p = Join-Path $b $s; if (Test-Path $p) { return $p }
            }
        }
    }
    return $null
}
function Test-Python {
    foreach ($n in @('python.exe', 'py.exe')) {
        $p = Find-Tool $n
        if ($p -and $p -notmatch '\\WindowsApps\\') {
            try {
                & $p -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' 2>$null | Out-Null
                if ($LASTEXITCODE -eq 0) { return $p }
            } catch { }
        }
    }
    return $null
}

$Packages = @(
    @{ Id='Git.Git'; Existing=(Find-Git) },
    @{ Id='Python.Python.3.13'; Existing=(Test-Python) }
)
if (-not $SkipEditor) { $Packages += @{ Id='Microsoft.VisualStudioCode'; Existing=(Find-Code) } }
# Autodesk Fusion itself is installed through the official Autodesk installer, not a guessed WinGet ID.
$Winget = Find-Tool 'winget.exe'
$Failures = 0
foreach ($pkg in $Packages) {
    $id = $pkg.Id
    if ($pkg.Existing) {
        Write-Host "KEEP $id : $($pkg.Existing)"
        $Records.Add(@{ package=$id; status='KEPT_EXISTING'; path=$pkg.Existing })
        continue
    }
    if (-not $Apply) {
        Write-Host "PLAN: verify with winget show, then install missing package $id"
        $Records.Add(@{ package=$id; status='PLANNED'; verified_in_catalog=$false })
        continue
    }
    if (-not $Winget) {
        $Records.Add(@{ package=$id; status='BLOCKED_USER_ACTION'; reason='WinGet missing' })
        $Failures++
        continue
    }
    $showArgs = @('show','--id',$id,'--exact','--source','winget','--disable-interactivity')
    if ($AcceptAgreements) { $showArgs += '--accept-source-agreements' }
    $showResult = Invoke-Captured $Winget $showArgs
    $showText = $showResult.Text
    $showCode = $showResult.Code
    Set-Content -LiteralPath (Join-Path $ReportDir ($id + '-show.txt')) -Value $showText -Encoding UTF8
    if ($showCode -ne 0) {
        $Records.Add(@{ package=$id; status='FAILED'; stage='catalog'; code=$showCode })
        $Failures++
        continue
    }
    $installArgs = @('install','--id',$id,'--exact','--source','winget','--no-upgrade')
    if ($AcceptAgreements) { $installArgs += @('--accept-source-agreements','--accept-package-agreements') }
    Write-Host "Installing $id. User interaction or UAC may be required."
    & $Winget @installArgs
    $installCode = $LASTEXITCODE
    $status = 'INSTALL_COMMAND_SUCCEEDED'
    if ($installCode -ne 0) { $status = 'FAILED'; $Failures++ }
    $Records.Add(@{ package=$id; status=$status; code=$installCode; runtime_verified=$false })
}
if (-not $SkipEditor) {
    $Code = Find-Code
    if ($Apply -and $Code) {
        $extensionList = Invoke-Captured $Code @('--list-extensions')
        $Extensions = @($extensionList.Text -split "`r?`n")
        $listCode = $extensionList.Code
        if ($listCode -ne 0) {
            $Failures++
            $Records.Add(@{ extension='openai.chatgpt'; status='FAILED'; stage='list'; code=$listCode })
        } elseif ($Extensions -contains 'openai.chatgpt') {
            $Records.Add(@{ extension='openai.chatgpt'; status='KEPT_EXISTING' })
        } else {
            & $Code --install-extension openai.chatgpt
            $extensionCode = $LASTEXITCODE
            if ($extensionCode -ne 0) { $Failures++ }
            $Records.Add(@{ extension='openai.chatgpt'; code=$extensionCode; runtime_verified=$false })
        }
    } elseif ($Apply) {
        $Failures++
        $Records.Add(@{ extension='openai.chatgpt'; status='BLOCKED_USER_ACTION'; reason='Reopen terminal or locate code.cmd' })
    } else { Write-Host 'PLAN: install the official openai.chatgpt extension if absent.' }
}
$summary = @{
    applied=[bool]$Apply; records=@($Records.ToArray()); failures=$Failures
    cad_runtime_verified=$false; next='Open a new terminal and follow docs/SETUP.md and docs/VALIDATION.md.'
}
$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $ReportDir 'summary.json') -Encoding UTF8
Write-Host "Report: $ReportDir"
Write-Host 'Autodesk Fusion installation, account sign-in, license and first GUI/API run remain manual gates.'
if ($Failures -gt 0) { throw "$Failures step(s) failed or are blocked. Inspect summary.json; do not mark setup complete." }
Write-Host 'Bootstrap finished. Installation exit codes are not CAD runtime validation.'
