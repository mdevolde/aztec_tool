@echo off

if "%1"=="check" goto check
if "%1"=="test" goto test
if "%1"=="doc" goto doc
if "%1"=="publish" goto publish

echo Usage: make.bat [check^|test^|doc^|publish]
exit /b 1

:check
uvx ruff@0.14.10 check .
if errorlevel 1 exit /b %errorlevel%

uvx ruff@0.14.10 format --check .
if errorlevel 1 exit /b %errorlevel%

uvx mypy@1.19.1
exit /b %errorlevel%

:test
call .venv\Scripts\activate && pytest
exit /b %errorlevel%

:doc
call .venv\Scripts\activate && uv run sphinx-apidoc -o docs\source\references aztec_tool
if errorlevel 1 exit /b %errorlevel%

call .venv\Scripts\activate && call docs\make.bat html
exit /b %errorlevel%

:publish
if exist dist\ rmdir /s /q dist\
if exist aztec_tool.egg-info\ rmdir /s /q aztec_tool.egg-info\

uv build
if errorlevel 1 exit /b %errorlevel%

uvx twine check .\dist\*
if errorlevel 1 exit /b %errorlevel%

uv publish
exit /b %errorlevel%
