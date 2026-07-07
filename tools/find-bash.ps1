# Locate Git's bash.exe (never the System32 launcher, which starts WSL) and
# print its path with forward slashes and no trailing newline - ready to drop
# into the Makefile's SHELL. Prints nothing if not found, so callers can decide
# how to report the failure. Shared by the Makefile and install-bash.ps1.
#
# PATH is read from the registry (Machine + User) rather than this process's
# environment so a bash installed in another session - but not yet on an already
# running terminal's PATH - is still discoverable without restarting the terminal.

$ErrorActionPreference = "SilentlyContinue"

function Find-Bash {
    $regPath = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
               [Environment]::GetEnvironmentVariable("Path", "User")

    foreach ($dir in ($regPath -split ";" | Where-Object { $_ })) {
        if ($dir -like "*System32*") { continue }
        $candidate = Join-Path $dir "bash.exe"
        if (Test-Path $candidate) { return $candidate }
    }

    # Derive from git.exe: walk up to the Git root and look for its bin\bash.exe
    # (git.exe may live in cmd\, bin\, or mingw64\bin\ depending on the install).
    $git = Get-Command git.exe -ErrorAction SilentlyContinue
    if ($git) {
        $dir = Split-Path $git.Source
        while ($dir -and -not (Test-Path (Join-Path $dir "bin\bash.exe"))) {
            $parent = Split-Path $dir
            $dir = if ($parent -eq $dir) { $null } else { $parent }
        }
        if ($dir) { return (Join-Path $dir "bin\bash.exe") }
    }

    # Well-known install locations.
    foreach ($p in @(
        "$env:ProgramFiles\Git\bin\bash.exe",
        "${env:ProgramFiles(x86)}\Git\bin\bash.exe",
        "$env:LocalAppData\Programs\Git\bin\bash.exe"
    )) {
        if ($p -and (Test-Path $p)) { return $p }
    }
}

$bash = Find-Bash
if ($bash) { $bash.Replace('\', '/') }
