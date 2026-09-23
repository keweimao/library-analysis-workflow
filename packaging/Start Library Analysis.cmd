@echo off
cd /d "%~dp0"
"%~dp0LibraryAnalysis\LibraryAnalysis.exe" start
set "result=%errorlevel%"
echo.
if not "%result%"=="0" (
  echo Startup did not finish. Review the error above.
  pause
)
exit /b %result%
