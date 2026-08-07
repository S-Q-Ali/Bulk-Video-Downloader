; Q-S-Ali Media Downloader — Inno Setup script (v2.0.0)
; Per-user install (no admin), bundles ffmpeg.exe for merging.

#define MyAppName "Q-S-Ali Media Downloader"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "S-Q-Ali"
#define MyAppURL "https://github.com/S-Q-Ali/Bulk-Video-Downloader"
#define MyAppExeName "Q-S-Ali Media Downloader.exe"

[Setup]
AppId={{03d871b7-5dd8-4e41-849b-47a0b7c08c87}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\Q-S-Ali Media Downloader
DefaultGroupName=Q-S-Ali Media Downloader
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=.
OutputBaseFilename=Q-S-Ali-Media-Downloader-Setup-2.0.0
SetupIconFile=..\src\qsali_media_downloader\resources\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName}
VersionInfoCopyright={#MyAppPublisher}
CloseApplications=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "portable\Q-S-Ali Media Downloader.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "portable\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "staging\bin\ffmpeg.exe"; DestDir: "{app}\bin"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
