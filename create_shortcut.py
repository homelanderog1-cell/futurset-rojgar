import os
import subprocess

desktop_dirs = [
    os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Desktop'),
    os.path.join(os.environ['USERPROFILE'], 'Desktop')
]

for desktop in desktop_dirs:
    if not os.path.exists(desktop):
        continue
    
    print(f"\n--- Setting up shortcuts in: {desktop} ---")
    
    # 1. Standard Windows Internet Shortcut (.url)
    url_file = os.path.join(desktop, "FuturSet Rojgar Portal.url")
    url_content = """[InternetShortcut]
URL=http://127.0.0.1:8000/
IconIndex=14
IconFile=C:\\Windows\\System32\\shell32.dll
"""
    with open(url_file, "w", encoding="utf-8") as f:
        f.write(url_content)
    print(f"[OK] Created URL shortcut: {url_file}")

    # 2. Smart Launcher Batch file that checks if server is up, starts it if not, and opens browser
    bat_file = os.path.join(desktop, "Start FuturSet Rojgar.bat")
    bat_content = """@echo off
title FuturSet Rojgar Portal
echo Checking FuturSet server status on port 8000...
netstat -ano | findstr :8000 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Server is offline. Starting FuturSet server in background...
    start /min "" "C:\\Users\\jashp\\anaconda3\\python.exe" "C:\\Users\\jashp\\.gemini\\antigravity\\scratch\\futurset-jobs\\run.py"
    timeout /t 2 /nobreak >nul
)
echo Opening FuturSet Rojgar Portal in your default browser...
start http://127.0.0.1:8000/
"""
    with open(bat_file, "w", encoding="utf-8") as f:
        f.write(bat_content)
    print(f"[OK] Created Batch Launcher: {bat_file}")

    # 3. Create Windows .lnk Shortcut
    lnk_file = os.path.join(desktop, "FuturSet Rojgar.lnk")
    ps_script = f"""
$wscript = New-Object -ComObject WScript.Shell
$shortcut = $wscript.CreateShortcut('{lnk_file}')
$shortcut.TargetPath = '{bat_file}'
$shortcut.WorkingDirectory = 'C:\\Users\\jashp\\.gemini\\antigravity\\scratch\\futurset-jobs'
$shortcut.IconLocation = 'C:\\Windows\\System32\\shell32.dll, 14'
$shortcut.Description = 'FuturSet Rojgar - Central and Gujarat Government Recruitment Portal'
$shortcut.Save()
"""
    res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[OK] Created Windows Shell Shortcut (.lnk): {lnk_file}")
    else:
        print("[ERR] PowerShell error:", res.stderr)
