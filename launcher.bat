@echo off
REM This script activates the Conda environment and runs the GUI.

REM This is typically: C:\Users\YOUR_USERNAME\anaconda3\Scripts
set CONDA_BASE_SCRIPTS="C:\Users\%USERNAME%\anaconda3\Scripts"

REM --- IMPORTANT: Configure these paths ---
REM Set the name of your Conda environment
set CONDA_ENV_NAME="video_object_count"

REM Set the path to your gui.py script's directory
REM Make sure to use backslashes and double quotes if the path contains spaces
set SCRIPT_DIR="%~dp0"
REM Example if gui.py is directly in the same folder as this .bat file
REM set SCRIPT_DIR="%~dp0"
REM If gui.py is in a subfolder, e.g., 'src', you'd set:
REM set SCRIPT_DIR="%~dp0src"

REM --- DO NOT EDIT BELOW THIS LINE UNLESS YOU KNOW WHAT YOU'RE DOING ---

echo Activating Conda environment: %CONDA_ENV_NAME%
call %CONDA_BASE_SCRIPTS%\activate.bat %CONDA_ENV_NAME%

if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate Conda environment. Make sure %CONDA_ENV_NAME% exists and CONDA_BASE_SCRIPTS path is correct.
    pause
    exit /b %ERRORLEVEL%
)

echo Running gui.py...
pushd %SCRIPT_DIR%
pythonw gui.py
popd