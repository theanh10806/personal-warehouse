# Create AppxManifest.xml + placeholder Assets for Microsoft Store.
# Run ONCE from repo root:
#   powershell -ExecutionPolicy Bypass -File packaging\init-store-assets.ps1
#
# Identity values come from Partner Center > Product management > Product identity.
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Partner Center identity (DO NOT EDIT unless you create a new product)
# ---------------------------------------------------------------------------
$identityName          = "Shinnosuke.ShinWarehouseManagement"
$publisher             = "CN=08A55B90-7F96-4488-8586-F75F7BCC7746"
$publisherDisplayName  = "Shinnosuke"
$appDisplayName        = "Shin Warehouse Management"

$pkgDir   = $PSScriptRoot
$assetDir = Join-Path $pkgDir "Assets"
$manifest = Join-Path $pkgDir "AppxManifest.xml"

# UTF-8 without BOM (makeappx requirement)
$utf8NoBom = New-Object System.Text.UTF8Encoding $false

# Read version from Python
$version = python -c "from personal_warehouse import __version__; print(__version__)"
if ($LASTEXITCODE -ne 0 -or -not $version) { throw "Cannot read version from personal_warehouse." }
$msixVersion = if ($version -match '^\d+\.\d+\.\d+\.\d+$') { $version } else { "$version.0" }

# --- Generate AppxManifest.xml (NO BOM) ---
$xml = @"
<?xml version="1.0" encoding="utf-8"?>
<Package
    xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
    xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
    xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities"
    IgnorableNamespaces="uap rescap">

  <Identity
      Name="$identityName"
      Publisher="$publisher"
      Version="$msixVersion"
      ProcessorArchitecture="x64" />

  <Properties>
    <DisplayName>$appDisplayName</DisplayName>
    <PublisherDisplayName>$publisherDisplayName</PublisherDisplayName>
    <Logo>Assets\StoreLogo.png</Logo>
    <Description>Personal inventory manager</Description>
  </Properties>

  <Dependencies>
    <TargetDeviceFamily
        Name="Windows.Desktop"
        MinVersion="10.0.17763.0"
        MaxVersionTested="10.0.22621.0" />
  </Dependencies>

  <Resources>
    <Resource Language="en-us" />
  </Resources>

  <Applications>
    <Application
        Id="PersonalWarehouse"
        Executable="PersonalWarehouse.exe"
        EntryPoint="Windows.FullTrustApplication">
      <uap:VisualElements
          DisplayName="$appDisplayName"
          Description="Personal inventory manager"
          BackgroundColor="transparent"
          Square150x150Logo="Assets\Square150x150Logo.png"
          Square44x44Logo="Assets\Square44x44Logo.png">
        <uap:DefaultTile
            Wide310x150Logo="Assets\Wide310x150Logo.png"
            Square310x310Logo="Assets\LargeTile.png" />
      </uap:VisualElements>
    </Application>
  </Applications>

  <Capabilities>
    <rescap:Capability Name="runFullTrust" />
    <Capability Name="internetClient" />
  </Capabilities>
</Package>
"@

[System.IO.File]::WriteAllText($manifest, $xml, $utf8NoBom)
Write-Host "Created: $manifest"
Write-Host "  Identity/Name      : $identityName"
Write-Host "  Identity/Publisher : $publisher"
Write-Host "  PublisherDisplayName: $publisherDisplayName"
Write-Host "  Version            : $msixVersion"

# --- Generate 5 placeholder PNGs (skip if already exist) ---
New-Item -ItemType Directory -Force -Path $assetDir | Out-Null
Add-Type -AssemblyName System.Drawing

$sizes = @{
    'StoreLogo.png'         = @(50, 50)
    'Square44x44Logo.png'   = @(44, 44)
    'Square150x150Logo.png' = @(150, 150)
    'Wide310x150Logo.png'   = @(310, 150)
    'LargeTile.png'         = @(310, 310)
}

foreach ($name in $sizes.Keys) {
    $outPath = Join-Path $assetDir $name
    if (Test-Path $outPath) {
        Write-Host "  = Assets\$name (already exists, kept)"
        continue
    }
    $w, $h = $sizes[$name]
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g   = [System.Drawing.Graphics]::FromImage($bmp)
    $g.Clear([System.Drawing.Color]::FromArgb(0, 120, 212))
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $fontSize = [Math]::Max(10, [int]($w / 6))
    $font  = New-Object System.Drawing.Font "Arial", $fontSize, ([System.Drawing.FontStyle]::Bold)
    $brush = [System.Drawing.Brushes]::White
    $sf = New-Object System.Drawing.StringFormat
    $sf.Alignment     = [System.Drawing.StringAlignment]::Center
    $sf.LineAlignment = [System.Drawing.StringAlignment]::Center
    $rect = New-Object System.Drawing.RectangleF 0, 0, $w, $h
    $g.DrawString("PW", $font, $brush, $rect, $sf)
    $g.Dispose()
    $bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
    Write-Host "  + Assets\$name ($w x $h)"
}

Write-Host ""
Write-Host "Done. Next:"
Write-Host "  powershell -ExecutionPolicy Bypass -File packaging\build.ps1"