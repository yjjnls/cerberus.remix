@echo OFF

REM
REM  THIS SHOULD BE COPIED TO CERBERUS ROOT
REM 
set __dir__=%~dp0
set __bash__=%__dir__%\MinGW\msys\1.0\bin\bash.exe
if not exist %__bash__% (
   echo "You may not run setup,please run scripts/setup/windows.ps1"
   pause
   exit 1
)
pushd %__dir__%
if "x%1" == "x" ( %__bash__%  --init-file init.sh ) else %__bash__%  %1
popd