Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c C:\Path\To\ZomboidTracker\start_monitor.bat", 0, False
Set WshShell = Nothing
