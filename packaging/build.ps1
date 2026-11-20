# Build Windows app: EXE installer + MSIX package for Microsoft Store.
# Run from repo root:
#   powershell -ExecutionPolicy Bypass -File packaging\build.ps1
#
# Optional code signing (NOT needed for Microsoft Store):
#   $env:CODE_SIGN_PFX      = "C:\secure\cert.pfx"
#   $env:CODE_SIGN_PASSWORD = "password"
#   or $env:CODE_SIGN_THUMBPRINT = "ABCDEF0123..."
param([switch]$RequireBothPackages)
$ErrorActionPreference = "Stop"

# ============================================================================
# 0. CHECK PYTHON
# ============================================================================
function Assert-Command($Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' not found. Install Python 3.9+ and add to PATH."
    }
}
Assert-Command "python"

$pyVer = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$p = $pyVer.Split('.')
if ([int]$p[0] -lt 3 -or ([int]$p[0] -eq 3 -and [int]$p[1] -lt 9)) {
    throw "Python 3.9+ required; found $pyVer. Python 3.12 recommended."
}

python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }
python -m pip install ".[all]" pyinstaller
if ($LASTEXITCODE -ne 0) { throw "Installing dependencies failed." }

# ============================================================================
# 1. READ VERSION
# ============================================================================
$version = python -c "from personal_warehouse import __version__; print(__version__)"
if ($LASTEXITCODE -ne 0 -or -not $version) { throw "Cannot read application version." }
if ($version -notmatch '^\d+\.\d+\.\d+$') { throw "Use the same stable major.minor.patch version for GitHub and Store." }
$msixVersion = "$version.0"
Write-Host "Building Personal Warehouse $version (MSIX: $msixVersion) with Python $pyVer"

# ============================================================================
# 2. CLEAN + PYINSTALLER
# ============================================================================
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\packaging\msix-staging -ErrorAction SilentlyContinue

# App icon: run `python packaging\make_icons.py my_icon.png` once; the .ico is then part of the repo.
$iconIco = Join-Path (Get-Location) "src\personal_warehouse\webui\static\icon.ico"
$iconArgs = @()
if (Test-Path $iconIco) { $iconArgs = @("--icon", $iconIco) } else { throw "icon.ico not found. Run packaging\make_icons.py before building." }
if (-not (Test-Path "src\personal_warehouse\webui\static\icon.png")) { throw "icon.png not found. Restore the application logo before building." }

python -m PyInstaller --noconfirm --clean --windowed --onedir `
    @iconArgs `
    --name PersonalWarehouse `
    --paths src `
    --collect-submodules personal_warehouse `
    --collect-all cv2 `
    --collect-all webview `
    --add-data "src\personal_warehouse\webui\static;personal_warehouse\webui\static" `
    --hidden-import PIL._tkinter_finder `
    packaging\run_app.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed." }

$appExe = Join-Path (Get-Location) "dist\PersonalWarehouse\PersonalWarehouse.exe"
if (-not (Test-Path $appExe)) { throw "PyInstaller did not create $appExe" }
Write-Host "Application folder: dist\PersonalWarehouse"

# ============================================================================
# 3. CODE SIGNING HELPERS (optional, NOT needed for Store)
# ============================================================================
function Resolve-SignToolPath {
    $c = Get-Command signtool -ErrorAction SilentlyContinue
    if ($c) { return $c.Source }
    $kits = "${env:ProgramFiles(x86)}\Windows Kits\10\bin"
    if (Test-Path $kits) {
        return (Get-ChildItem $kits -Recurse -Filter signtool.exe -EA SilentlyContinue |
                Where-Object { $_.FullName -match '\\x64\\signtool\.exe$' } |
                Select-Object -First 1).FullName
    }
    return $null
}

function Invoke-CodeSign {
    param([string]$FilePath)
    if (-not (Test-Path $FilePath)) { throw "File not found: $FilePath" }
    $st = Resolve-SignToolPath
    if (-not $st) { Write-Warning "signtool.exe not found. Skipping: $FilePath"; return $false }
    $a = @("sign", "/fd", "SHA256", "/tr", "http://timestamp.digicert.com", "/td", "SHA256", "/v")
    if ($env:CODE_SIGN_THUMBPRINT) {
        $a += @("/sha1", $env:CODE_SIGN_THUMBPRINT, "/s", "My")
    } elseif ($env:CODE_SIGN_PFX) {
        $a += @("/f", $env:CODE_SIGN_PFX)
        if ($env:CODE_SIGN_PASSWORD) { $a += @("/p", $env:CODE_SIGN_PASSWORD) }
    } else {
        Write-Warning "No signing certificate configured. Skipping: $FilePath"
        return $false
    }
    $a += $FilePath
    Write-Host "Signing: $FilePath"
    & $st @a
    if ($LASTEXITCODE -ne 0) { throw "signtool failed: $FilePath" }
    & $st verify /pa /v $FilePath
    if ($LASTEXITCODE -ne 0) { throw "Signature verification failed: $FilePath" }
    Write-Host "Signed OK: $FilePath"
    return $true
}

$signingAvailable = [bool]($env:CODE_SIGN_PFX -or $env:CODE_SIGN_THUMBPRINT)
if (-not $signingAvailable) {
    Write-Host "No signing certificate configured - artifacts will be UNSIGNED."
    Write-Host "For Microsoft Store: no signing needed, Store re-signs after approval."
}

if ($signingAvailable) {
    Write-Host "=== Signing application executable ==="
    Invoke-CodeSign $appExe | Out-Null
}

# ============================================================================
# 4. EXE INSTALLER (Inno Setup - for GitHub / offline)
# ============================================================================
$iscc = (Get-Command iscc -EA SilentlyContinue).Source
if (-not $iscc) {
    $iscc = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
    ) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
}

if ($iscc) {
    & $iscc "/DAppVersion=$version" "packaging\installer.iss"
    if ($LASTEXITCODE -ne 0) { throw "Inno Setup compilation failed." }

    $installer = Join-Path (Get-Location) "Output\PersonalWarehouse-Setup-$version.exe"
    if (-not (Test-Path $installer)) { throw "Installer not created: $installer" }

    if ($signingAvailable) {
        Write-Host "=== Signing installer ==="
        Invoke-CodeSign $installer | Out-Null
    }
    Write-Host "Installer: $installer"
} else {
    if ($RequireBothPackages) { throw "Inno Setup is required for a unified release." }
    Write-Warning "Inno Setup 6 not found. Skipping EXE installer."
}

# ============================================================================
# 5. MSIX FOR MICROSOFT STORE
# ============================================================================
function Resolve-MakeAppxPath {
    $c = Get-Command makeappx -EA SilentlyContinue
    if ($c) { return $c.Source }
    $kits = "${env:ProgramFiles(x86)}\Windows Kits\10\bin"
    if (Test-Path $kits) {
        return (Get-ChildItem $kits -Recurse -Filter makeappx.exe -EA SilentlyContinue |
                Where-Object { $_.FullName -match '\\x64\\makeappx\.exe$' } |
                Select-Object -First 1).FullName
    }
    return $null
}

$makeappx     = Resolve-MakeAppxPath
$manifestPath = ".\packaging\AppxManifest.xml"
$assetsPath   = ".\packaging\Assets"

if (-not $makeappx) {
    if ($RequireBothPackages) { throw "Windows SDK makeappx.exe is required for a unified release." }
    Write-Warning "makeappx.exe not found. Skipping MSIX."
    Write-Host "Install Windows SDK: https://developer.microsoft.com/windows/downloads/windows-sdk/"
} elseif (-not (Test-Path $manifestPath)) {
    if ($RequireBothPackages) { throw "Store manifest is required for a unified release." }
    Write-Warning "Missing $manifestPath. Run packaging\init-store-assets.ps1 first."
} else {
    Write-Host "=== Building MSIX package ==="
    $staging = ".\packaging\msix-staging"
    Remove-Item -Recurse -Force $staging -EA SilentlyContinue
    New-Item -ItemType Directory -Force -Path "$staging\Assets" | Out-Null

    Copy-Item ".\dist\PersonalWarehouse\*" $staging -Recurse -Force
    $sourceFiles = Get-ChildItem ".\dist\PersonalWarehouse" -Recurse -File
    foreach ($sourceFile in $sourceFiles) {
        $relative = $sourceFile.FullName.Substring((Resolve-Path ".\dist\PersonalWarehouse").Path.Length + 1)
        $copiedFile = Join-Path $staging $relative
        if ((Get-FileHash $sourceFile.FullName -Algorithm SHA256).Hash -ne (Get-FileHash $copiedFile -Algorithm SHA256).Hash) {
            throw "Store payload differs from EXE payload: $relative"
        }
    }

    # ---------------------------------------------------------------------
    # Read manifest at BYTE level so we can strip a UTF-8 BOM if present.
    # File.ReadAllText can leave BOM bytes behind on some PS 5.1 builds.
    # ---------------------------------------------------------------------
    $manifestFull = (Resolve-Path $manifestPath).Path
    $bytes = [System.IO.File]::ReadAllBytes($manifestFull)
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        Write-Host "Stripping UTF-8 BOM from source manifest"
        $bytes = $bytes[3..($bytes.Length - 1)]
    }
    $manifestXml = [System.Text.Encoding]::UTF8.GetString($bytes)

    # Replace Version ONLY inside <Identity ...> (NOT MinVersion/MaxVersionTested)
    $manifestXml = [regex]::Replace(
        $manifestXml,
        '(<Identity\b[^>]*?\bVersion=")[^"]*(")',
        ('${1}' + $msixVersion + '${2}')
    )

    # Write WITHOUT BOM
    $utf8NoBom      = New-Object System.Text.UTF8Encoding $false
    $stagingManifest = Join-Path $staging "AppxManifest.xml"
    [System.IO.File]::WriteAllText($stagingManifest, $manifestXml, $utf8NoBom)

    # Verify staging manifest has no BOM
    $check = [System.IO.File]::ReadAllBytes($stagingManifest)
    if ($check.Length -ge 3 -and $check[0] -eq 0xEF -and $check[1] -eq 0xBB -and $check[2] -eq 0xBF) {
        throw "Staging manifest still has BOM after write - aborting"
    }
    Write-Host ("Staging manifest OK - first bytes: {0:X2} {1:X2} {2:X2}" -f $check[0], $check[1], $check[2])

    if (Test-Path $assetsPath) {
        Copy-Item "$assetsPath\*" "$staging\Assets" -Recurse -Force
    } else {
        Write-Warning "Missing Assets folder. MSIX will fail. Run init-store-assets.ps1."
    }

    $msixOut = Join-Path (Get-Location) "Output\PersonalWarehouse-$version.msix"
    New-Item -ItemType Directory -Force -Path (Split-Path $msixOut) | Out-Null
    & $makeappx pack /d $staging /p $msixOut /o
    if ($LASTEXITCODE -ne 0) { throw "makeappx pack failed." }
    Write-Host "MSIX (upload Store): $msixOut"

    if ($signingAvailable) {
        Write-Host "=== Signing MSIX (optional, only for offline test) ==="
        Invoke-CodeSign $msixOut | Out-Null
    }
}

# ============================================================================
# 6. SHA256 CHECKSUMS
# ============================================================================
$outDir = Join-Path (Get-Location) "Output"
if (Test-Path $outDir) {
    $files = Get-ChildItem $outDir -File | Where-Object { $_.Extension -eq '.exe' -or $_.Extension -eq '.msix' }
    if ($files) {
        $lines = foreach ($f in $files) {
            $h = (Get-FileHash $f.FullName -Algorithm SHA256).Hash
            "$h  $($f.Name)"
        }
        $lines | Out-File (Join-Path $outDir "SHA256SUMS.txt") -Encoding ASCII
        Write-Host "Checksums: Output\SHA256SUMS.txt"
    }
}

Write-Host ""
Write-Host "=== BUILD COMPLETE ==="
Write-Host "Portable app : dist\PersonalWarehouse\"
if ($iscc)     { Write-Host "EXE installer: Output\PersonalWarehouse-Setup-$version.exe" }
if ($makeappx) { Write-Host "MSIX (Store) : Output\PersonalWarehouse-$version.msix" }
