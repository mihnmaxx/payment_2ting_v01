@echo off
REM Kích hoạt môi trường ảo
call venv\Scripts\activate.bat

REM Khởi động các dịch vụ
start cmd /k "cd /d %~dp0 && venv\Scripts\activate && python manage.py runserver"
start cmd /k "cd /d %~dp0 && venv\Scripts\activate && python manage.py listen_firebird"
start cmd /k "ngrok http 8000"

REM Đợi ngrok khởi động
timeout /t 5

REM Cập nhật URL
python update_env.py

REM Giữ cửa sổ cmd mở
cmd /k
