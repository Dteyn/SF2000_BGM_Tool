@echo off
set ver=0.2.0
:: build script for the distributable versions of kerokero
:: requires: PyInstaller, 7-zip Extra (Standalone console version) - https://7-zip.org/a/7z2408-extra.7z
:: credit: EricGoldsteinNz (author of tadpole) and tzlion (author of frogtool)
:: source: https://github.com/EricGoldsteinNz/tadpole/blob/main/build.bat
:: source: https://github.com/tzlion/frogtool/blob/main/build.bat
if not exist "venv\" (
    python -m venv venv
)
if not exist "venv\Lib\site-packages\PyInstaller" (
    venv\Scripts\python -m pip install pyinstaller
)
if not exist "venv\Lib\site-packages\PIL" (
    venv\Scripts\python -m pip install Pillow
)
if not exist "venv\Lib\site-packages\PyQt5" (
    venv\Scripts\python -m pip install PyQt5
)
pyinstaller kerokero.py -n kerokero-%ver%.exe -F --icon kerokero.ico --clean --noconsole --version-file versioninfo --add-data="kerokero.ico;." --add-data="README.md;."

echo.
echo Done building .EXE. Moving on to packaging...
echo.

copy README.md "dist\readme.md"
:: extremely dirty markdown to txt conversion by stripping out a few non-obvious characters
py -c "open('dist/readme.txt','w').write(open('dist/readme.md','r').read().replace('`','').replace('### ','').replace('## ','').replace('# ','').replace('**','').replace('shell',''))"
copy LICENSE "dist\license.txt"
copy requirements.txt "dist\requirements.txt"
copy kerokero.py "dist\kerokero.py"
copy kerokero.py "dist\kerokero.pyw"
copy kerokero.svg "dist\kerokero.svg"
copy install-required-packages.bat "dist\install-required-packages.bat"
cd dist

:: package .zip files
7za a Kerokero-win-v%ver%.zip kerokero-%ver%.exe kerokero.pyw kerokero.svg readme.txt license.txt requirements.txt install-required-packages.bat
7za a Kerokero-python-v%ver%.zip kerokero.py kerokero.svg readme.txt license.txt requirements.txt install-required-packages.bat
cd ..

:: cleanup
del dist\readme.md
del dist\readme.txt
del dist\license.txt
del dist\requirements.txt
del dist\kerokero.py
del dist\kerokero.pyw
del dist\kerokero.svg
del dist\install-required-packages.bat
del kerokero-%ver%.exe.spec

echo Done!
pause