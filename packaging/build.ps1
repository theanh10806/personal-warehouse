# Build the Windows app (and installer when Inno Setup 6 is installed).
# Run from the repository root:
#   powershell -ExecutionPolicy Bypass -File packaging\build.ps1
$ErrorActionPreference = "Stop"

function Assert-Command($Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found. Install Python 3.9+ and ensure it is on PATH."
    }
}

Assert-Command "python"
$pythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$versionParts = $pythonVersion.Split('.')
if ([int]$versionParts[0] -lt 3 -or ([int]$versionParts[0] -eq 3 -and [int]$versionParts[1] -lt 9)) {
    throw "Python 3.9 or newer is required; found $pythonVersion. Python 3.12 is recommended for release builds."
}

python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }
python -m pip install ".[all]" pyinstaller
if ($LASTEXITCODE -ne 0) { throw "Installing application/build dependencies failed." }

$version = python -c "from personal_warehouse import __version__; print(__version__)"
if ($LASTEXITCODE -ne 0 -or -not $version) { throw "Could not read the application version." }
Write-Host "Building Personal Warehouse $version with Python $pythonVersion"

# Remove stale outputs so an old EXE cannot accidentally be packaged.
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

python -m PyInstaller --noconfirm --clean --windowed --onedir `
    --name PersonalWarehouse `
    --paths src `
    --collect-submodules personal_warehouse `
    --collect-all cv2 `
<<<<<<< HEAD
    --collect-all webview `
    --add-data "src\personal_warehouse\webui\static;personal_warehouse\webui\static" `
=======
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
    --hidden-import PIL._tkinter_finder `
    packaging\run_app.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed." }

$appExe = Join-Path (Get-Location) "dist\PersonalWarehouse\PersonalWarehouse.exe"
if (-not (Test-Path $appExe)) { throw "PyInstaller did not create $appExe" }
Write-Host "Application folder: dist\PersonalWarehouse"

# Locate Inno Setup 6. A folder build is still useful if Inno Setup is not installed.
$isccPath = (Get-Command iscc -ErrorAction SilentlyContinue).Source
if (-not $isccPath) {
    $candidates = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
    )
    $isccPath = $candidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
}

if ($isccPath) {
    & $isccPath "/DAppVersion=$version" "packaging\installer.iss"
    if ($LASTEXITCODE -ne 0) { throw "Inno Setup compilation failed." }
    $installer = Join-Path (Get-Location) "Output\PersonalWarehouse-Setup-$version.exe"
    if (-not (Test-Path $installer)) { throw "Installer was not created: $installer" }
    Write-Host "Installer created: $installer"
} else {
    Write-Warning "Inno Setup 6 not found. The EXE folder was built, but no installer was created."
    Write-Host "Install Inno Setup 6 from https://jrsoftware.org/isdl.php, then run this script again."
}
