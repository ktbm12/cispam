[Setup]
AppName=CISPAM
AppVersion=1.0
AppPublisher=CISPAM
DefaultDirName={autopf}\CISPAM
DefaultGroupName=CISPAM
OutputDir=dist\installer
OutputBaseFilename=CISPAM_Setup
SetupIconFile=cispam\static\images\favicons\favicon.ico
Compression=lzma2
SolidCompression=yes
; Require admin rights for Program Files installation
PrivilegesRequired=admin

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Include the entire onedir output folder
Source: "dist\CISPAM\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\CISPAM"; Filename: "{app}\CISPAM.exe"; IconFilename: "{app}\CISPAM.exe"
Name: "{commondesktop}\CISPAM"; Filename: "{app}\CISPAM.exe"; IconFilename: "{app}\CISPAM.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\CISPAM.exe"; Description: "{cm:LaunchProgram,CISPAM}"; Flags: nowait postinstall skipifsilent
