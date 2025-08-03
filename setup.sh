# Django Database Migrations Management Scripts

# Create migrations for the CyberQuest models
python manage.py makemigrations cyberquest

# Apply migrations to the database
python manage.py migrate

# Create a superuser for admin access
python manage.py createsuperuser

# Load initial data fixtures
python manage.py loaddata initial_categories.json
python manage.py loaddata initial_badges.json
python manage.py loaddata sample_questions.json

# Collect static files for production
python manage.py collectstatic --noinput

# Run the development server
python manage.py runserver 0.0.0.0:8000
