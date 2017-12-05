@echo OFF

powershell Set-ExecutionPolicy RemoteSigned
if %ERRORLEVEL% neq 0 (
   echo "You should use adminstrator to run the bat."
   pause
   exit/b 1
) 


powershell -file %~dp0\windows.ps1
if %ERRORLEVEL% neq 0 (
   echo "Install MinGW Failed!"
   pause
   exit/b 1
) 

pushd %~dp0\..\..
bash.bat python scripts/setup/installer.py
set ret=%ERRORLEVEL%
popd
pause
exit/b %ret%
