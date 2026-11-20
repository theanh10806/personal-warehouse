; Inno Setup script - EXE installer for GitHub / offline.
; Microsoft Store does NOT use this file (Store uses MSIX).
; Build: ISCC /DAppVersion=3.1.0 packaging\installer.iss
;
; AppId must never change - it lets new installers upgrade old installs.
; User data lives in Documents\MyWarehouse and is NOT touched by install/uninstall.
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{6F1D2B7A-3C54-4E8B-9A21-5D7C0E4B8F13}
AppName=Personal Warehouse
AppVerName=Personal Warehouse {#AppVersion}
AppVersion={#AppVersion}
AppPublisher=Vo The Anh
AppPublisherURL=https://github.com/theanh10806/personal-warehouse
AppSupportURL=https://github.com/theanh10806/personal-warehouse/issues
DefaultDirName={autopf}\Personal Warehouse
DefaultGroupName=Personal Warehouse
DisableProgramGroupPage=yes
AllowNoIcons=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.17763
OutputDir=..\Output
OutputBaseFilename=PersonalWarehouse-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
#if FileExists("..\src\personal_warehouse\webui\static\icon.ico")
SetupIconFile=..\src\personal_warehouse\webui\static\icon.ico
#endif
UninstallDisplayIcon={app}\PersonalWarehouse.exe
UninstallDisplayName=Personal Warehouse {#AppVersion}
CloseApplications=yes
RestartApplications=no
AppMutex=PersonalWarehouseSingleInstance

VersionInfoVersion={#AppVersion}
VersionInfoCompany=Personal Warehouse
VersionInfoDescription=Personal Warehouse Installer
VersionInfoProductName=Personal Warehouse
VersionInfoProductVersion={#AppVersion}
VersionInfoCopyright=(c) 2026 Personal Warehouse

#ifdef BuildSignToolName
SignTool={#BuildSignToolName}
SignedUninstaller=yes
#endif

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Shortcuts:"

[Files]
Source: "..\dist\PersonalWarehouse\*"; DestDir: "{app}"; \
  Flags: recursesubdirs createallsubdirs ignoreversion; \
  Excludes: "__pycache__\*, *.pyc, *.pyo, *.pdb, *.chm"

[Icons]
Name: "{group}\Personal Warehouse"; Filename: "{app}\PersonalWarehouse.exe"
Name: "{autodesktop}\Personal Warehouse"; Filename: "{app}\PersonalWarehouse.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\PersonalWarehouse.exe"; Description: "Launch Personal Warehouse"; \
  Flags: nowait postinstall skipifsilent
; In-app update: the app starts this installer with /SILENT /RELAUNCH=1. Reopen the app when it finishes.
Filename: "{app}\PersonalWarehouse.exe"; Flags: nowait; Check: RelaunchRequested

[Code]
function RelaunchRequested: Boolean;
begin
  Result := ExpandConstant('{param:RELAUNCH|0}') = '1';
end;
