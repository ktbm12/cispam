[Setup]
AppName=CISPAM
AppVersion=1.0
DefaultDirName={autopf}\CISPAM
DefaultGroupName=CISPAM
OutputDir=dist\installer
OutputBaseFilename=CISPAM_Setup
SetupIconFile=cispam\static\images\favicons\favicon.ico
Compression=lzma2
SolidCompression=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\CISPAM.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\CISPAM"; Filename: "{app}\CISPAM.exe"
Name: "{commondesktop}\CISPAM"; Filename: "{app}\CISPAM.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\CISPAM.exe"; Description: "{cm:LaunchProgram,CISPAM}"; Flags: nowait postinstall skipifsilent
