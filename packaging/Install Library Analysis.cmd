@echo off
cd /d "%~dp0"
"%~dp0LibraryAnalysis\LibraryAnalysis.exe" install
set "result=%errorlevel%"
echo.
if not "%result%"=="0" echo Installation did not finish. Review the error above.
pause
exit /b %result%
