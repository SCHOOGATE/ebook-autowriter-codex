$ws = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath("Desktop")
$sc = $ws.CreateShortcut("$desktop\BookDownload.lnk")
$sc.TargetPath = "C:\Users\user\repos\ebook-autowriter-codex\scripts\download_book.bat"
$sc.WorkingDirectory = "C:\Users\user\repos\ebook-autowriter-codex"
$sc.IconLocation = "shell32.dll,56"
$sc.Save()
Write-Host "Shortcut created on Desktop"
