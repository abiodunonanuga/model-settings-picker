$ErrorActionPreference = 'Stop'
try {
    $pickerRoot = Split-Path -Parent $PSScriptRoot
    $candidates = @()
    if ($env:MODEL_SETTINGS_PICKER_PYTHON) {
        $candidates = @($env:MODEL_SETTINGS_PICKER_PYTHON)
    } else {
        $candidates += Join-Path $HOME '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
        $pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
        if ($pythonCommand -and $pythonCommand.Source -notmatch 'WindowsApps') {
            $candidates += $pythonCommand.Source
        }
    }
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            & $candidate -c 'import sys; sys.exit(sys.version_info < (3,10))' 2>$null
            if ($LASTEXITCODE -eq 0) {
                & $candidate (Join-Path $pickerRoot 'picker.py') hook
                exit $LASTEXITCODE
            }
        }
    }
    throw 'Python 3.10+ is unavailable; complete plugin setup.'
} catch {
    [Console]::Out.Write('{"systemMessage":"Model Settings Picker runtime unavailable; continuing without a gate. Complete plugin setup."}')
    exit 0
}
