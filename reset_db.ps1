# Elimina la base de datos actual (SQLite)
Remove-Item db.sqlite3

# Elimina todas las migraciones
Get-ChildItem -Recurse -Path *\migrations\* -Include *.py -Exclude __init__.py | Remove-Item
Get-ChildItem -Recurse -Path *\migrations\* -Include *.pyc | Remove-Item

# Crear nuevas migraciones y aplicarlas
python manage.py makemigrations
python manage.py migrate

# Cargar datos iniciales si es necesario
# python manage.py loaddata your_fixture.json

# Crear superusuario
python manage.py createsuperuser
