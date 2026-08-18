# Ensure Git bash and GNU make are available, refreshing them to the latest
# version when already installed. -IfMissing leaves what is already installed
# alone, so CI (whose runners ship Git) skips the winget round-trip.
param([switch]$IfMissing)

$ErrorActionPreference = "Stop"

function Install-Latest($id, $probe) {
    if ($IfMissing -and (& $probe)) { return }

    # `winget install` upgrades a package that is already present, and exits
    # non-zero when it is already current; neither is an error here.
    winget install --id $id -e --source winget --disable-interactivity `
        --accept-package-agreements --accept-source-agreements 2>&1 |
        Where-Object { $_ -notmatch "No available upgrade found|No newer package versions are available|Found an existing package already installed" }
    $global:LASTEXITCODE = 0
}

Install-Latest "Git.Git" { [bool](& "$PSScriptRoot\find-bash.ps1") }
Install-Latest "ezwinports.make" { [bool](Get-Command make.exe -ErrorAction SilentlyContinue) }

$bash = & "$PSScriptRoot\find-bash.ps1"

if (-not $bash -or -not (Test-Path $bash)) {
    throw "Could not locate Git bash.exe. Ensure Git for Windows installed correctly."
}

$bashDir = Split-Path $bash
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")

# Persist on PATH for future shell instances...
if (($userPath -split ";") -notcontains $bashDir) {
    $userPath = if ($userPath) { "$bashDir;$userPath" } else { $bashDir }
    [Environment]::SetEnvironmentVariable("Path", $userPath, "User")
}

# ...and in this shell now, without a restart. Prepended so it wins over the
# System32 bash.exe that launches WSL.
$env:Path = $bashDir + ";" +
    [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + $userPath
