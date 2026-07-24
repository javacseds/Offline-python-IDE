; =============================================================================
; GITAMW Python Smart IDE — Inno Setup Installer Script
; Gouthami Institute of Technology and Management for Women (Autonomous)
; Department of Computer Science & Engineering
;
; HOW TO USE:
;   1. First run build_exe.bat (or python build_exe.py) to produce the PyInstaller dist/
;   2. Download & install Inno Setup from https://jrsoftware.org/isdl.php
;   3. Open THIS file in Inno Setup Compiler and click Build → Compile
;   4. The final Setup_GITAMW_Python_IDE.exe will be in installer\setup_output\
; =============================================================================

#define AppName       "GITAMW Python Smart IDE"
#define AppVersion    "1.0.0"
#define AppPublisher  "Dept. of CSE, GITAMW"
#define AppURL        "https://github.com/javacseds/Offline-python-IDE"
#define AppExeName    "GITAMW_Smart_IDE.exe"
#define AppMutex      "GITAMW_Python_Smart_IDE_Mutex_v1"

[Setup]
; Basic installer settings
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} v{#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; Default install directory
DefaultDirName={autopf}\GITAMW Python Smart IDE
DefaultGroupName={#AppName}
AllowNoIcons=yes

; Output
OutputDir=setup_output
OutputBaseFilename=Setup_GITAMW_Python_IDE_v{#AppVersion}

; Appearance
SetupIconFile=assets\icon.ico
WizardStyle=modern
WizardImageFile=assets\wizard_banner.bmp
WizardSmallImageFile=assets\wizard_icon.bmp

; Compression
Compression=lzma2/ultra64
SolidCompression=yes

; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Windows version requirement
MinVersion=6.1sp1

; Uninstall
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}

; Misc
DisableProgramGroupPage=yes
DisableReadyMemo=no
ShowLanguageDialog=no
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";   Description: "Create a &Desktop shortcut";    GroupDescription: "Additional icons:"; Flags: checkedonce
Name: "startmenuicon"; Description: "Create a &Start Menu shortcut"; GroupDescription: "Additional icons:"; Flags: checkedonce
Name: "quicklaunch";   Description: "Create a &Quick Launch shortcut (taskbar pin)"; GroupDescription: "Additional icons:"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; Copy the entire PyInstaller-generated folder
Source: "dist\GITAMW_Smart_IDE\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Desktop shortcut
Name: "{autodesktop}\{#AppName}";        Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"; Tasks: desktopicon; Comment: "Launch GITAMW Python Smart IDE"

; Start Menu shortcut
Name: "{group}\{#AppName}";              Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"; Tasks: startmenuicon; Comment: "Launch GITAMW Python Smart IDE"
Name: "{group}\Uninstall {#AppName}";   Filename: "{uninstallexe}";       Tasks: startmenuicon

[Run]
; Launch the app after installation (optional)
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName} now"; Flags: nowait postinstall skipifsilent shellexec

[UninstallRun]
; Kill running instance before uninstall
Filename: "taskkill.exe"; Parameters: "/F /IM {#AppExeName}"; Flags: runhidden skipifdoesntexist; RunOnceId: "KillApp"

[Code]
// ─── Check for existing running instance before install ──────────────────
function IsMutexActive(const MutexName: String): Boolean;
var
  hMutex: THandle;
begin
  hMutex := CreateMutex(False, MutexName);
  Result := (GetLastError() = 183);  // ERROR_ALREADY_EXISTS
  if hMutex <> 0 then CloseHandle(hMutex);
end;

function InitializeSetup(): Boolean;
begin
  if IsMutexActive('{#AppMutex}') then
  begin
    MsgBox(
      '{#AppName} is currently running.' + #13#10 +
      'Please close it (via the system tray icon → Quit) before installing.',
      mbError, MB_OK
    );
    Result := False;
    Exit;
  end;
  Result := True;
end;

// ─── Welcome page extra message ──────────────────────────────────────────
function GetWelcomeLabel(Param: String): String;
begin
  Result :=
    'Welcome to the {#AppName} Installer!' + #13#10 + #13#10 +
    'This will install the offline Python IDE on your computer.' + #13#10 +
    'No internet connection is required to run the IDE.' + #13#10 + #13#10 +
    'Developed by: Dept. of CSE' + #13#10 +
    'Gouthami Institute of Technology and Management for Women (Autonomous)';
end;
