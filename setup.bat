@echo off
echo ========================================
echo BidNest Setup Script
echo ========================================
echo.

echo Step 1: Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error creating virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully!
echo.

echo Step 2: Activating virtual environment...
call venv\Scripts\activate
echo.

echo Step 3: Upgrading pip...
python -m pip install --upgrade pip
echo.

echo Step 4: Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error installing dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

echo Step 5: Checking for .env file...
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file and add your configuration!
    echo.
)
echo.

echo Step 6: Running migrations...
python manage.py makemigrations
python manage.py migrate
if errorlevel 1 (
    echo Error running migrations
    echo Make sure PostgreSQL is running and database is created
    pause
    exit /b 1
)
echo Migrations completed successfully!
echo.

echo Step 7: Creating static files directory...
if not exist static mkdir static
if not exist static\css mkdir static\css
if not exist static\js mkdir static\js
if not exist static\images mkdir static\images
echo.

echo Step 8: Collecting static files...
python manage.py collectstatic --noinput
echo.

echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Create a superuser: python manage.py createsuperuser
echo 3. Run the server: python manage.py runserver
echo.
echo For Celery tasks (optional):
echo - celery -A bidnest worker -l info
echo - celery -A bidnest beat -l info
echo.
pause
