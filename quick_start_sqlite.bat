@echo off
echo ========================================
echo BidNest Quick Start with SQLite
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Running migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo Creating superuser...
echo Please create an admin account:
python manage.py createsuperuser

echo.
echo Collecting static files...
python manage.py collectstatic --noinput

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Starting development server...
echo Server will be available at: http://127.0.0.1:8000/
echo Admin panel: http://127.0.0.1:8000/admin/
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver
