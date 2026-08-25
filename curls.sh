curl "http://127.0.0.1:8000/api/reports/orm-report/?status=PAID&search=Cliente"
curl "http://127.0.0.1:8000/api/reports/product-ranking/"
curl "http://127.0.0.1:8000/api/reports/raw-report/?status=PAID"
curl "http://127.0.0.1:8000/api/reports/summary/"

curl -X POST http://127.0.0.1:8000/api/reports/insert-sql/ -H "Content-Type: application/json" -d "{\"customer_id\":1,\"product_id\":1,\"quantity\":2}"
curl -X POST http://127.0.0.1:8000/api/reports/bulk-update/ -H "Content-Type: application/json" -d "{\"from_status\":\"PENDING\",\"to_status\":\"PAID\"}"
curl -X POST http://127.0.0.1:8000/api/reports/cleanup/ -H "Content-Type: application/json" -d "{\"confirm\":true}"
# Solo PostgreSQL / Docker
curl -X POST http://127.0.0.1:8000/api/reports/call-procedure/ -H "Content-Type: application/json" -d "{\"customer_id\":1}"
