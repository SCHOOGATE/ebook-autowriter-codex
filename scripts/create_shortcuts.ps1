$ws = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath("Desktop")
$scriptDir = Split-Path -Parent $PSCommandPath
$repoDir = Split-Path -Parent $scriptDir
$userName = $env:USERNAME

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

# Chrome (book creation) - DevTools debug mode (default port 9222)
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (Test-Path $chromePath) {
    $port = if ($env:CDTP_PORT) { $env:CDTP_PORT } else { "9222" }
    $profileDir = "C:\Users\$userName\chrome-profiles\profile-$port"
    $sc3 = $ws.CreateShortcut("$desktop\Chrome book creation.lnk")
    $sc3.TargetPath = $chromePath
    $sc3.Arguments = "--remote-debugging-port=$port --remote-allow-origins=* --user-data-dir=`"$profileDir`" https://chatgpt.com"
    $sc3.WorkingDirectory = "C:\Program Files\Google\Chrome\Application"
    $sc3.Description = "Codex CLI Chrome DevTools port $port"
    $sc3.Save()
    Write-Host "Chrome book creation shortcut created (port: $port, user: $userName)"
} else {
    Write-Host "WARNING: Chrome not found at $chromePath. Skipping Chrome shortcut."
}
