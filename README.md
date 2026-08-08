# URL Shortener API

This is a simple URL shortener API built with FastAPI. It supports custom slugs, expiration, and provides analytics.

## Endpoints

### Shorten URL

**POST** `/shorten`

Request body:
```json
{
  "url": "https://example.com",
  "slug": "customslug",
  "expiration": "2023-12-31T23:59:59"
}
```

Example curl command:
```bash
curl -X POST http://localhost:8000/shorten -H "Content-Type: application/json" -d '{"url": "https://example.com", "slug": "customslug", "expiration": "2023-12-31T23:59:59"}'
```

### Get Original URL

**GET** `/r/{slug}`

Example curl command:
```bash
curl http://localhost:8000/r/customslug
```

### Get Analytics

**GET** `/analytics/{slug}`

Example curl command:
```bash
curl http://localhost:8000/analytics/customslug
```
