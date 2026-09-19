@echo off
title FuturSet Jobs Portal - Launcher
cd /d "C:\Users\jashp\.gemini\antigravity\scratch\futurset-jobs"
echo ========================================================
echo        FuturSet - Government Job Finding Portal
echo ========================================================
echo.
echo Starting FuturSet Web Application & Scanner Engine...
echo Opening in browser: http://127.0.0.1:8000
echo Gujarat Portal: http://127.0.0.1:8000/gujarat
echo B.Tech CSE Hub: http://127.0.0.1:8000/btech-cse
echo.

start "" "http://127.0.0.1:8000"
"C:\Users\jashp\anaconda3\python.exe" run.py
pause

