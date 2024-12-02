@echo off
REM Activate the virtual environment
call "C:\Users\adeni\OneDrive - ylblz\Upwork\TataCars\venv\Scripts\activate.bat"

REM Navigate to the project directory
cd /d "C:\Users\adeni\OneDrive - ylblz\Upwork\TataCars"

REM Run the Python script and redirect output to a log file
python cron_job.py >> "C:\Users\adeni\OneDrive - ylblz\Upwork\TataCars\cron_job.log" 2>&1

REM Deactivate the virtual environment (optional)
deactivate