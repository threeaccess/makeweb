param(
    [switch]$buildsite,
    [switch]$force,
    [Parameter(ValueFromRemainingArguments)]
    [string[]]$Remaining
)

$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonBin = if ($env:PYTHON_BIN) { $env:PYTHON_BIN } else { 'python' }

$PyArgs = @()
if ($buildsite) { $PyArgs += '--buildsite' }
if ($force) { $PyArgs += '--force' }
if ($Remaining) { $PyArgs += $Remaining }

& $PythonBin "$ScriptDir\make_web.py" @PyArgs
