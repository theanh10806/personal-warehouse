; Inno Setup script. Version is passed on the command line: ISCC /DAppVersion=3.0.0 installer.iss
; Keep AppId unchanged forever - it is how a new installer recognises and upgrades an old install.
; User data lives in Documents\MyWarehouse and is NOT touched by install, upgrade or uninstall.
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{6F1D2B7A-3C54-4E8B-9A21-5D7C0E4B8F13}
AppName=Personal Warehouse
AppVersion={#AppVersion}
AppPublisher=Personal Warehouse
DefaultDirName={autopf}\Personal Warehouse
DefaultGroupName=Personal Warehouse
PrivilegesRequired=lowest
OutputDir=..\Output
OutputBaseFilename=PersonalWarehouse-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\PersonalWarehouse.exe
CloseApplications=yes

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Shortcuts:"

[Files]
Source: "..\dist\PersonalWarehouse\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\Personal Warehouse"; Filename: "{app}\PersonalWarehouse.exe"
Name: "{autodesktop}\Personal Warehouse"; Filename: "{app}\PersonalWarehouse.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\PersonalWarehouse.exe"; Description: "Launch Personal Warehouse"; Flags: nowait postinstall skipifsilent
