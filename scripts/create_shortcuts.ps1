$ws = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath("Desktop")
$scriptDir = Split-Path -Parent $PSCommandPath
$repoDir = Split-Path -Parent $scriptDir

# BookDownload（Codex Cloud用）
$sc1 = $ws.CreateShortcut("$desktop\BookDownload.lnk")
$sc1.TargetPath = Join-Path $scriptDir "download_book.bat"
$sc1.WorkingDirectory = $repoDir
$sc1.IconLocation = "shell32.dll,56"
$sc1.Save()
Write-Host "BookDownload shortcut created"

# BookRestore（Codex CLI用）
$sc2 = $ws.CreateShortcut("$desktop\BookRestore.lnk")
$sc2.TargetPath = Join-Path $scriptDir "restore_book.bat"
$sc2.WorkingDirectory = $repoDir
$sc2.IconLocation = "shell32.dll,3"
$sc2.Save()
Write-Host "BookRestore shortcut created"
