@echo off
cd /d "%~dp0"

IF NOT EXIST ".git" (
    git init
    git branch -M main
)

git add .
git commit -m "Initial release: A desktop Tkinter tool for computational exploration of **prime gaps** and the conjectures that govern them"

git remote get-url origin >nul 2>&1
IF ERRORLEVEL 1 (
    gh repo create mhawarey/prime-gap-explorer --public --source=. --remote=origin --push
) ELSE (
    git push -u origin main
)

echo [DONE] https://github.com/mhawarey/prime-gap-explorer
pause
