Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
appPath = fso.BuildPath(scriptDir, "forza_music_overlay.py")
venvPythonw = fso.BuildPath(scriptDir, ".venv\Scripts\pythonw.exe")
venvPython = fso.BuildPath(scriptDir, ".venv\Scripts\python.exe")

If fso.FileExists(venvPythonw) Then
    pythonExe = venvPythonw
ElseIf fso.FileExists(venvPython) Then
    pythonExe = venvPython
Else
    pythonExe = "pythonw.exe"
End If

command = Chr(34) & pythonExe & Chr(34) & " " & Chr(34) & appPath & Chr(34)
shell.Run command, 1, False
