# Aula de consultas Django: ORM, SQL y PostgreSQL

Proyecto educativo: una tienda filtra ventas, calcula indicadores y realiza operaciones administrativas con ORM y SQL directo. Funciona con SQLite local y PostgreSQL mediante Docker.

## Resultados de aprendizaje cubiertos

| Requisito | Implementación |
| --- | --- |
| 5.1 ORM con filtros | `orm-report/`: `filter`, `Q`, rangos, `exclude`, `select_related` y `defer` |
| ORM personalizado | `product-ranking/`: `values`, `annotate`, `Count` y `Sum` |
| Índices | índices sobre email, nombre, precio, fecha y estado en modelos |
| 5.2 SQL recuperación | `raw-report/`: `raw()` parametrizado y mapeado a `Sale`; `summary/`: cursor |
| 5.3 SQL CRUD | `insert-sql/` (CREATE), `bulk-update/` (UPDATE), `cleanup/` (DELETE) |
| Procedimiento almacenado | `call-procedure/`, migración `0002` para PostgreSQL |

El SQL siempre usa placeholders `%s` y parámetros separados: no concatena entrada de usuario.

## Docker (recomendado)

```bash
docker compose up --build
```

Disponible en `http://localhost:8000`; administrador en `/admin/`. El arranque aplica migraciones y crea el superusuario inicial `admin` / `admin12345`. Cambia esas variables antes de desplegar:

```bash
DJANGO_SUPERUSER_USERNAME=profesor
DJANGO_SUPERUSER_EMAIL=profesor@example.com
DJANGO_SUPERUSER_PASSWORD=una-clave-segura
```

Puedes partir copiando `.env.example` a `.env`; el archivo `.env` no se versiona.

Carga datos demostrativos:

```bash
docker compose exec web python manage.py seed_data
```

## Local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Sin configuración PostgreSQL se utiliza SQLite. El procedimiento almacenado se demuestra únicamente con PostgreSQL/Docker.

## Endpoints

| Método | Ruta | Cuerpo o filtro |
| --- | --- | --- |
| GET | `/api/reports/orm-report/` | `?status=PAID&search=Cliente&start_date=2026-01-01T00:00:00Z` |
| GET | `/api/reports/product-ranking/` | anotaciones ORM |
| GET | `/api/reports/raw-report/` | `?status=PAID` |
| GET | `/api/reports/summary/` | resumen SQL con cursor |
| POST | `/api/reports/insert-sql/` | `{"customer_id":1,"product_id":1,"quantity":2}` |
| POST | `/api/reports/bulk-update/` | `{"from_status":"PENDING","to_status":"PAID"}` |
| POST | `/api/reports/cleanup/` | `{"confirm":true}` |
| POST | `/api/reports/call-procedure/` | `{"customer_id":1}` |

Las mutaciones requieren POST. Revisa [curls.sh](curls.sh) para ejemplos ejecutables.
