$ws = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath("Desktop")

# BookDownload（Codex Cloud用）
$sc1 = $ws.CreateShortcut("$desktop\BookDownload.lnk")
$sc1.TargetPath = "C:\Users\user\repos\ebook-autowriter-codex\scripts\download_book.bat"
$sc1.WorkingDirectory = "C:\Users\user\repos\ebook-autowriter-codex"
$sc1.IconLocation = "shell32.dll,56"
$sc1.Save()
Write-Host "BookDownload shortcut created"

# BookRestore（Codex CLI用）
$sc2 = $ws.CreateShortcut("$desktop\BookRestore.lnk")
$sc2.TargetPath = "C:\Users\user\repos\ebook-autowriter-codex\scripts\restore_book.bat"
$sc2.WorkingDirectory = "C:\Users\user\repos\ebook-autowriter-codex"
$sc2.IconLocation = "shell32.dll,3"
$sc2.Save()
Write-Host "BookRestore shortcut created"
