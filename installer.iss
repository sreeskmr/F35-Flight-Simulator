[Setup]
AppName=F35 Throttle System
AppVersion=1.0
DefaultDirName={pf}\F35Throttle
DefaultGroupName=F35 Throttle
UninstallDisplayIcon={app}\F35.exe
OutputDir=dist
OutputBaseFilename=F35_Installer
LicenseFile=LICENSE
SetupIconFile=src\F35.ico
Compression=lzma
SolidCompression=yes

[Files]
Source: "src\dist\F35.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\F35.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\vjoy-config.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\F35_Throttle_Button_Map.csv"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\F35 Throttle"; Filename: "{app}\F35.exe"
Name: "{commondesktop}\F35 Throttle"; Filename: "{app}\F35.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional options:"

[Run]
Filename: "{app}\F35.exe"; Description: "Launch F35 Throttle after install"; Flags: nowait postinstall skipifsilent
