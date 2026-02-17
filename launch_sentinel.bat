@echo off
title License Sentinel Launcher
echo 🛡️ Starting License Sentinel Pro Suite...

:: Start the Streamlit Dashboard in a new window
start cmd /k "streamlit run app.py"

:: Start the Automation Engine in a new window
start cmd /k "python scheduler.py"

echo ✅ Both services are launching in separate windows.
pause