# Run tools/uv.sh under Git bash (located via find-bash.ps1), forwarding all args to uv.
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$bash = & (Join-Path $scriptDir "find-bash.ps1")
if (-not $bash) {
    Write-Error "Could not locate Git bash - run tools/install-bash.ps1 (open a new terminal if you just installed it)"
    exit 1
}

& $bash (Join-Path $scriptDir "uv.sh") @args
exit $LASTEXITCODE
