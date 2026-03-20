# Postman Collection Examples

Complete set of API examples for Postman testing.

## Import to Postman

You can import this as a Postman collection or use the examples below.

## Environment Variables

Create a Postman environment with:

```
base_url: http://localhost:8000
api_v1: http://localhost:8000/api/v1
job_id: (will be set automatically from upload response)
```

---

## 1. Health Check

**GET** `{{base_url}}/health`

**Response:**
```json
{
    "status": "healthy",
    "service": "Sales Analytics API",
    "version": "1.0.0"
}
```

---

## 2. Upload CSV File

**POST** `{{api_v1}}/upload-transactions`

**Body:** form-data
- Key: `file`
- Type: File
- Value: [Select your CSV file]

**Tests (Postman):**
```javascript
var jsonData = pm.response.json();
pm.environment.set("job_id", jsonData.job_id);
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});
```

**Response:**
```json
{
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "pending",
    "message": "File uploaded successfully. Processing has started.",
    "created_at": "2024-01-20T10:30:00Z"
}
```

---

## 3. Check Job Status

**GET** `{{api_v1}}/jobs/{{job_id}}`

**Response:**
```json
{
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "filename": "transactions.csv",
    "total_rows": 10000,
    "processed_rows": 10000,
    "progress_percentage": 100.0,
    "error_message": null,
    "created_at": "2024-01-20T10:30:00Z",
    "started_at": "2024-01-20T10:30:05Z",
    "completed_at": "2024-01-20T10:31:23Z"
}
```

---

## 4. Get Total Sales (No Filters)

**GET** `{{api_v1}}/sales/total`

**Response:**
```json
{
    "fecha_inicio": null,
    "fecha_fin": null,
    "total_sales": 5678900.50,
    "total_orders": 10000,
    "average_order_value": 567.89
}
```

---

## 5. Get Total Sales (Date Range)

**GET** `{{api_v1}}/sales/total?fecha_inicio=2024-01-01&fecha_fin=2024-12-31`

**Query Params:**
- `fecha_inicio`: 2024-01-01
- `fecha_fin`: 2024-12-31

**Response:**
```json
{
    "fecha_inicio": "2024-01-01",
    "fecha_fin": "2024-12-31",
    "total_sales": 5234567.89,
    "total_orders": 9500,
    "average_order_value": 551.01
}
```

---

## 6. Get Monthly Trend

**GET** `{{api_v1}}/sales/monthly-trend`

**Response:**
```json
{
    "data": [
        {
            "year": 2024,
            "month": 1,
            "total_sales": 450000.00,
            "order_count": 850,
            "avg_order_value": 529.41
        },
        {
            "year": 2024,
            "month": 2,
            "total_sales": 480000.00,
            "order_count": 900,
            "avg_order_value": 533.33
        }
    ]
}
```

---

## 7. Get Department Analytics

**GET** `{{api_v1}}/analytics/departments`

**Response:**
```json
{
    "data": [
        {
            "id_departamento": "DEPT001",
            "total_sales": 1200000.00,
            "order_count": 2000,
            "percentage_of_total": 21.13
        },
        {
            "id_departamento": "DEPT002",
            "total_sales": 1100000.00,
            "order_count": 1900,
            "percentage_of_total": 19.37
        }
    ]
}
```

---

## 8. Get Section Analytics

**GET** `{{api_v1}}/analytics/sections`

**Response:**
```json
{
    "data": [
        {
            "id_seccion": "SEC001",
            "id_departamento": "DEPT001",
            "total_sales": 800000.00,
            "order_count": 1500,
            "percentage_of_total": 14.08
        }
    ]
}
```

---

## 9. Get Top Products by Quantity

**GET** `{{api_v1}}/analytics/products/top-quantity?limit=10`

**Query Params:**
- `limit`: 10

**Response:**
```json
{
    "data": [
        {
            "id_producto": "PROD001",
            "nombre_producto": "Laptop Dell XPS 15",
            "total_quantity": 1500,
            "total_revenue": 1950000.00,
            "order_count": 1500,
            "avg_unit_price": 1300.00
        }
    ],
    "limit": 10
}
```

---

## 10. Get Top Products by Revenue

**GET** `{{api_v1}}/analytics/products/top-revenue?limit=10`

**Query Params:**
- `limit`: 10

**Response:**
```json
{
    "data": [
        {
            "id_producto": "PROD005",
            "nombre_producto": "MacBook Pro 16\"",
            "total_quantity": 800,
            "total_revenue": 2000000.00,
            "order_count": 800,
            "avg_unit_price": 2500.00
        }
    ],
    "limit": 10
}
```

---

## 11. Get Top Customers

**GET** `{{api_v1}}/analytics/customers/top?limit=20`

**Query Params:**
- `limit`: 20

**Response:**
```json
{
    "data": [
        {
            "id_cliente": "CUST001",
            "total_spent": 25000.00,
            "order_count": 15,
            "average_order_value": 1666.67,
            "first_purchase": "2024-01-15",
            "last_purchase": "2024-12-28"
        }
    ],
    "limit": 20
}
```

---

## 12. Get Customer Average Spend

**GET** `{{api_v1}}/analytics/customers/average-spend`

**Response:**
```json
{
    "average_spend_per_customer": 5678.90,
    "total_customers": 1000,
    "total_sales": 5678900.00
}
```

---

## 13. Get Order Count

**GET** `{{api_v1}}/analytics/orders/count`

**Response:**
```json
{
    "total_orders": 10000,
    "average_order_value": 567.89,
    "total_sales": 5678900.00
}
```

---

## 14. Get Average Order Value

**GET** `{{api_v1}}/analytics/orders/average-value`

**Response:**
```json
{
    "total_orders": 10000,
    "average_order_value": 567.89,
    "total_sales": 5678900.00
}
```

---

## Error Handling Examples

### Invalid File Type

**POST** `{{api_v1}}/upload-transactions`

**Body:** form-data (text file instead of CSV)

**Response: 400 Bad Request**
```json
{
    "detail": "Only CSV files are accepted"
}
```

### Job Not Found

**GET** `{{api_v1}}/jobs/00000000-0000-0000-0000-000000000000`

**Response: 404 Not Found**
```json
{
    "detail": "Job 00000000-0000-0000-0000-000000000000 not found"
}
```

### Invalid Date Range

**GET** `{{api_v1}}/sales/total?fecha_inicio=2024-12-31&fecha_fin=2024-01-01`

**Response: 400 Bad Request**
```json
{
    "detail": "fecha_inicio must be before or equal to fecha_fin"
}
```

---

## Postman Collection JSON

Save this as a `.json` file and import to Postman:

```json
{
    "info": {
        "name": "Sales Analytics API",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "Health Check",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/health",
                    "host": ["{{base_url}}"],
                    "path": ["health"]
                }
            }
        },
        {
            "name": "Upload Transactions",
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "exec": [
                            "var jsonData = pm.response.json();",
                            "pm.environment.set(\"job_id\", jsonData.job_id);"
                        ]
                    }
                }
            ],
            "request": {
                "method": "POST",
                "header": [],
                "body": {
                    "mode": "formdata",
                    "formdata": [
                        {
                            "key": "file",
                            "type": "file",
                            "src": []
                        }
                    ]
                },
                "url": {
                    "raw": "{{api_v1}}/upload-transactions",
                    "host": ["{{api_v1}}"],
                    "path": ["upload-transactions"]
                }
            }
        },
        {
            "name": "Get Job Status",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{api_v1}}/jobs/{{job_id}}",
                    "host": ["{{api_v1}}"],
                    "path": ["jobs", "{{job_id}}"]
                }
            }
        }
    ]
}
```

---

## Testing Workflow

1. **Health Check** - Verify API is running
2. **Upload CSV** - Upload your data file (saves job_id)
3. **Poll Job Status** - Check status until completed
4. **Run Analytics** - Execute all analytics endpoints
5. **Verify Results** - Check data makes sense

## Tips

- Use Postman environment variables for `base_url` and `job_id`
- Set up tests to automatically save the `job_id` from upload response
- Create a test runner to execute all analytics endpoints sequentially
- Use Postman monitors to run health checks periodically
