@echo off
cd /d "%~dp0"
python forza_telemetry_simulator.py
if errorlevel 1 pause
