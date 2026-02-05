$ErrorActionPreference = "Stop"
try {
    $WshShell = New-Object -comObject WScript.Shell
    $DesktopPath = [Environment]::GetFolderPath("Desktop")
    $ShortcutPath = Join-Path $DesktopPath "Marketing AI.lnk"
    
    $CurrentDir = Get-Location
    $TargetFile = Join-Path $CurrentDir "launch_app.vbs"
    
    if (-not (Test-Path $TargetFile)) {
        Write-Error "Could not find launch_app.vbs in the current directory."
    }

    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $TargetFile
    $Shortcut.WorkingDirectory = $CurrentDir.Path
    $Shortcut.Description = "Start Marketing AI Application"
    $Shortcut.IconLocation = "shell32.dll,3" # Folder icon or generic app icon
    $Shortcut.Save()
    
    Write-Host "Success: Shortcut 'Marketing AI' created on your Desktop."
} catch {
    Write-Error "Failed to create shortcut: $_"
}