@echo off
setlocal

:: Folder path
set "folder=C:\Path\To\Folder"

:: Get today's date in yyyyMMdd format
for /f %%a in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd"') do set "today=%%a"

:: Change to folder
pushd "%folder%" || (echo Folder not found: %folder% & exit /b)

:: Use for loop to check for file(s) matching the pattern *yyyyMMdd*.csv
set "found="
for %%F in (*%today%*.csv) do (
    echo Found file: %%F
    set "found=1"
)

:: Check if any file was found
if defined found (
    echo Matching file(s) exist.
) else (
    echo No matching file found for %today%.
)

popd
endlocal
