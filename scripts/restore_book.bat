@echo off
chcp 65001 >nul
echo ========================================
echo   書籍画像復元（Codex CLI用）
echo ========================================
echo.

cd /d "%USERPROFILE%\repos\ebook-autowriter-codex"

echo [1/2] 最新の書籍を検索中...
for /f "delims=" %%i in ('dir /b /ad /o-d output\ 2^>nul') do (
    set "SLUG=%%i"
    goto :found
)
echo エラー: outputフォルダに書籍が見つかりません。
pause
exit /b 1

:found
echo   → %SLUG% が見つかりました
echo.
echo [2/2] 画像を復元中...
python scripts\decode_binaries.py "output\%SLUG%"
echo.
echo ========================================
echo   完了！フォルダを開きます
echo ========================================
echo.
echo   原稿・メタデータ: output\%SLUG%\
echo   画像: output\%SLUG%\images\
echo.
explorer "output\%SLUG%"
pause
