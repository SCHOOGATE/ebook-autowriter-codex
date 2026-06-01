$ws = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath("Desktop")
$scriptDir = Split-Path -Parent $PSCommandPath
$repoDir = Split-Path -Parent $scriptDir

$sc = $ws.CreateShortcut("$desktop\BookDownload.lnk")
$sc.TargetPath = Join-Path $scriptDir "download_book.bat"
$sc.WorkingDirectory = $repoDir
$sc.IconLocation = "shell32.dll,56"
$sc.Save()
Write-Host "Shortcut created on Desktop"
