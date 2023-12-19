@echo off
set DJANGO_SETTINGS_MODULE=teethsite_backend.settings
gunicorn teethsite_backend.wsgi:application --bind 127.0.0.1:8001  --log-file=-
pause