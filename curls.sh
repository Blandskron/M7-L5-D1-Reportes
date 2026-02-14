# ==============================
# 1) REPORTE ORM (SIN FILTROS)
# ==============================
curl -X GET http://127.0.0.1:8000/api/reports/orm-report/


# ==============================
# 2) REPORTE ORM (CON FILTRO STATUS)
# ==============================
curl -X GET "http://127.0.0.1:8000/api/reports/orm-report/?status=PAID"


# ==============================
# 3) REPORTE ORM (BUSQUEDA PARCIAL)
# ==============================
curl -X GET "http://127.0.0.1:8000/api/reports/orm-report/?search=Cliente"


# ==============================
# 4) REPORTE ORM (RANGO FECHAS)
# ==============================
curl -X GET "http://127.0.0.1:8000/api/reports/orm-report/?start_date=2026-01-01T00:00:00&end_date=2026-12-31T23:59:59"


# ==============================
# 5) REPORTE SQL RAW
# ==============================
curl -X GET "http://127.0.0.1:8000/api/reports/raw-report/?status=PAID"


# ==============================
# 6) RESUMEN CON CURSOR SQL
# ==============================
curl -X GET http://127.0.0.1:8000/api/reports/summary/


# ==============================
# 7) BULK UPDATE SQL (PENDING -> PAID)
# ==============================
curl -X GET http://127.0.0.1:8000/api/reports/bulk-update/


# ==============================
# 8) DELETE CANCELLED (SQL)
# ==============================
curl -X GET http://127.0.0.1:8000/api/reports/cleanup/


# ==============================
# 9) INSERT DIRECTO POR SQL
# ==============================
curl -X GET http://127.0.0.1:8000/api/reports/insert-sql/


# ==============================
# 10) CALL STORED PROCEDURE
# ==============================
curl -X GET http://127.0.0.1:8000/api/reports/call-procedure/