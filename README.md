# Motor de Reportes de Ventas (ORM + SQL) — Tutorial Paso a Paso

## 1) Crear entorno virtual
```bash
python -m venv venv
venv\Scripts\activate
````

## 2) Instalar Django

```bash
python -m pip install --upgrade pip
pip install django
```

## 3) Crear proyecto Django

```bash
django-admin startproject config .
```

## 4) Crear app `reports`

```bash
python manage.py startapp reports
```

## 5) Copiar archivos del proyecto

Copia y pega estos archivos en tu proyecto (reemplazando los existentes si aplica):

* `reports/models.py`
* `reports/admin.py`
* `reports/views.py`
* `reports/urls.py`
* `config/urls.py`

Y crea el seeder:

* `reports/management/__init__.py`
* `reports/management/commands/__init__.py`
* `reports/management/commands/seed_data.py`

## 6) Registrar la app en `settings.py`

En `config/settings.py` agrega:

```python
INSTALLED_APPS = [
    ...
    "reports",
]
```

## 7) Crear y aplicar migraciones

```bash
python manage.py makemigrations
python manage.py makemigrations reports
python manage.py migrate
```

## 8) Crear superusuario (para entrar al admin)

```bash
python manage.py createsuperuser
```

## 9) Llenar la base de datos con mucha información

```bash
python manage.py seed_data
```

Datos masivos:

```bash
python manage.py seed_data --customers 1000 --products 500 --sales 20000
```

## 10) Levantar el servidor

```bash
python manage.py runserver
```

## 11) Probar endpoints (en el navegador)

### Reporte ORM (filtros)

* `http://127.0.0.1:8000/api/reports/orm-report/`

Ejemplo con filtros:

* `http://127.0.0.1:8000/api/reports/orm-report/?status=PAID`
* `http://127.0.0.1:8000/api/reports/orm-report/?search=Cliente`
* `http://127.0.0.1:8000/api/reports/orm-report/?start_date=2026-01-01T00:00:00&end_date=2026-12-31T23:59:59`

### Reporte SQL RAW

* `http://127.0.0.1:8000/api/reports/raw-report/?status=PAID`

### Resumen con cursor SQL

* `http://127.0.0.1:8000/api/reports/summary/`

### CRUD por SQL directo

* Bulk update (PENDING -> PAID):

  * `http://127.0.0.1:8000/api/reports/bulk-update/`
* Borrar CANCELLED:

  * `http://127.0.0.1:8000/api/reports/cleanup/`
* Insert por SQL:

  * `http://127.0.0.1:8000/api/reports/insert-sql/`

### Procedimiento almacenado (si existe en tu BD)

* `http://127.0.0.1:8000/api/reports/call-procedure/`

## 12) Admin Django

* `http://127.0.0.1:8000/admin/`
