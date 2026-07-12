# Zigma API — Test & Integration Guide

## 1. High-Level Architecture

```
┌──────────────┐     ┌────────────┐     ┌────────────────┐
│   Client      │────▶│   ALB /    │────▶│   Nginx (SSL)  │
│ (Mobile/Web)  │     │   CloudFront│     │  Rate Limit    │
└──────────────┘     └────────────┘     └───────┬────────┘
                                                │
                    ┌───────────────────────────┼───────────────────────────┐
                    │                           │                           │
                    ▼                           ▼                           ▼
          ┌─────────────────┐   ┌──────────────────────┐   ┌──────────────────┐
          │  Django API     │   │  Celery Workers      │   │  WebSocket GW    │
          │  (Gunicorn)     │   │  (async tasks)       │   │  (Go, future)    │
          │  REST endpoints │   │  - Order matching    │   │  Real-time push  │
          │  JWT auth       │   │  - AI inference      │   └──────────────────┘
          └────────┬────────┘   │  - Market data fetch │
                   │            └──────────┬───────────┘
                   ▼                       ▼
          ┌─────────────────────────────────────────┐
          │              Redis Cluster               │
          │  - Celery broker & result backend        │
          │  - Cache (market quotes, sessions)       │
          │  - Rate limiting counters                │
          └────────────────────┬────────────────────┘
                               │
                               ▼
          ┌─────────────────────────────────────────┐
          │         PostgreSQL 16 (Supabase)         │
          │  - All persistent state                  │
          │  - RLS for direct client reads           │
          └─────────────────────────────────────────┘
```

### Design Principles

- **CQRS:** Writes go through Django REST (commands). Real-time reads via WebSocket Gateway (separate Go service).
- **Single source of truth:** PostgreSQL holds all persistent state.
- **Event-driven:** State changes (order fill, deposit) produce events → Redis Pub/Sub → client.
- **Stateless:** Django, Celery, Gateway horizontally scalable behind load balancer.
- **ACID:** All write operations wrapped in `transaction.atomic()` with `select_for_update()` for financial integrity.

---

## 2. Authentication Flow

```
Client                          Django API
  │                                │
  ├── POST /api/v1/auth/register/  │  Body: {email, password, password2}
  │                                │  Response: {user, access, refresh}
  ├── POST /api/v1/auth/login/     │  Body: {email, password}
  │                                │  Response: {access, refresh, user}
  ├── GET  /api/v1/auth/me/        │  Header: Authorization: Bearer <access>
  │                                │  Response: {id, email}
  ├── POST /api/v1/auth/token/refresh/  │  Body: {refresh}
  │                                │  Response: {access}
  └── ...                          │
```

- **Access token:** 1 hour (HS256)
- **Refresh token:** 7 days
- **All authenticated endpoints** require `Authorization: Bearer <token>`

---

## 3. End-to-End User Flows

### Flow A: Onboarding (Register → KYC → Status)

```
1. POST /api/v1/auth/register/       →  JWT tokens + user
2. POST /api/v1/auth/login/          →  JWT tokens (or use register response)
3. POST /api/v1/kyc/upload/          →  Submit documents (document_type, urls)
4. GET  /api/v1/kyc/status/          →  {status: "SUBMITTED"} → poll until "APPROVED"
```

### Flow B: Funding (Deposit → Balance Check)

```
1. POST /api/v1/wallet/deposit/      →  Body: {amount_cents: 50000}
2. GET  /api/v1/wallet/              →  {balance_cents: 150000, currency: "USD"}
3. GET  /api/v1/wallet/transactions/ →  [{type: "DEPOSIT", amount_cents: 50000, ...}]
```

### Flow C: Stock Trading (Paper)

```
1. POST /api/v1/trading/orders/create/  →  Body: {symbol: "AAPL", side: "buy",
       order_type: "market", quantity: 10}
       Response: {status: "filled", filled_quantity: 10, ...}
2. GET  /api/v1/trading/holdings/       →  [{symbol: "AAPL", quantity: 10, ...}]
3. GET  /api/v1/trading/orders/         →  Query: ?status=filled
4. POST /api/v1/trading/orders/create/  →  Body: {symbol: "AAPL", side: "sell",
       order_type: "market", quantity: 10}
```

### Flow D: Crypto Buy/Sell (Fiat → Crypto → Fiat)

```
1. GET  /api/v1/wallet/               →  Check fiat balance
2. POST /api/v1/crypto/buy/           →  Body: {from_currency: "USD",
       to_currency: "BTC", amount_cents: 50000}
       Response: {crypto_amount, rate, balance_cents}
3. GET  /api/v1/crypto/holdings/      →  [{symbol: "BTC", quantity, ...}]
4. GET  /api/v1/crypto/wallets/       →  [{currency: "BTC", balance, ...}]
5. POST /api/v1/crypto/sell/          →  Body: {from_currency: "BTC",
       to_currency: "USD", quantity: 0.01}
       Response: {received_cents, rate, balance_cents}
```

### Flow E: Crypto Swap (Crypto → Crypto)

```
1. POST /api/v1/crypto/swaps/create/  →  Body: {from_currency: "BTC",
       to_currency: "ETH", from_amount: 0.1}
       Response: {to_amount, rate, status: "COMPLETED", ...}
2. GET  /api/v1/crypto/swaps/         →  List swaps
3. GET  /api/v1/crypto/wallets/       →  Verify BTC deducted, ETH credited
```

### Flow F: Banking (Account → Transfer → P2P)

```
1. POST /api/v1/banking/account/      →  Create virtual bank account
2. GET  /api/v1/banking/account/detail/ →  {account_number, balance_cents}
3. GET  /api/v1/banking/transactions/ →  List bank transactions
4. POST /api/v1/banking/transfer/     →  External bank transfer
5. POST /api/v1/banking/p2p/          →  Body: {recipient_email, amount_cents}
```

### Flow G: Virtual Cards (Issue → Freeze → Limits → Cancel)

```
1. POST /api/v1/banking/cards/create/ →  Body: {brand: "VISA"}
       Response: {last4, status: "ACTIVE", ...}
2. GET  /api/v1/banking/cards/        →  List cards
3. POST /api/v1/banking/cards/{id}/freeze/  →  Freeze card
4. POST /api/v1/banking/cards/{id}/limits/  →  Body: {daily_limit_cents: 100000}
5. POST /api/v1/banking/cards/{id}/toggle/online/  →  Body: {enabled: false}
6. POST /api/v1/banking/cards/{id}/unfreeze/  →  Unfreeze
7. POST /api/v1/banking/cards/{id}/cancel/   →  Cancel card permanently
```

### Flow H: AI Assistant (Chat → Analysis → Insight)

```
1. POST /api/v1/ai/chat/sessions/create/   →  Create session
2. POST /api/v1/ai/chat/sessions/{id}/messages/create/  →  Body: {content: "Analyze my portfolio"}
       Response: AI reply
3. GET  /api/v1/ai/chat/sessions/{id}/messages/  →  Message history
4. POST /api/v1/ai/portfolio/analyze/  →  Generate portfolio analysis
5. GET  /api/v1/ai/stock/insight/STOCK/AAPL  →  AI-generated insight
```

---

## 4. Robustness & Resilience

| Pattern | Implementation |
|---|---|
| **Database transactions** | `transaction.atomic()` wraps all financial operations |
| **Row-level locking** | `select_for_update()` on wallet/holding rows prevents race conditions |
| **Idempotent deposits** | Transaction reference field prevents duplicate processing |
| **Health checks** | `GET /api/v1/health/` checks DB + Redis connectivity |
| **Graceful degradation** | Market data falls back to REST poll if WebSocket disconnected |
| **Rate limiting** | Nginx (50 req/s) + DRF throttles (1000/hour user, 100/hour anonymous) |
| **Input validation** | Every serializer validates types, ranges, and cross-field constraints |
| **Error format** | Consistent `{error: {code, message}}` structure across all endpoints |
| **Caching** | Redis-backed `django-redis` cache 30s TTL for market data |
| **Connection pooling** | PostgreSQL `CONN_MAX_AGE=60`, Redis connection pool max 100 |

---

## 5. Scalability

| Component | Scale Strategy | Max Throughput |
|---|---|---|
| **Django API** | Horizontal (multiple Gunicorn workers per instance + multiple ECS tasks) | 10k req/s |
| **Celery workers** | Separate queues per priority; auto-scale by queue depth | 5k tasks/s |
| **PostgreSQL** | Supabase read replicas, connection pooling (PgBouncer) | 50k reads/s |
| **Redis** | ElastiCache cluster mode (sharded pub/sub + streams) | 100k msg/s |
| **Nginx** | Load-balanced across API tasks, SSL termination offload | 20k conn/s |
| **WebSocket Gateway** | Go service, 50k conns per instance (future) | 500k conns |

---

## 6. Testing Strategy

### 6.1 Running Tests

```bash
# Run all tests
pytest apps/ --cov=apps --cov-report=term-missing -v

# Run by app
pytest apps/wallet/tests/ -v
pytest apps/trading/tests/ -v
pytest apps/crypto/tests/ -v

# Run by marker
pytest -m "slow" -v

# Run with HTML coverage report
pytest --cov=apps --cov-report=html
```

### 6.2 Test Categories

| Category | What | Tools |
|---|---|---|
| **Unit** | Model methods, serializer validation, service functions | `pytest`, `factory_boy` |
| **Integration** | Full API endpoint testing (request → DB → response) | `APIClient`, `conftest` fixtures |
| **Auth** | JWT issuance, expiry, invalid/expired tokens | `APIClient` with malformed tokens |
| **Financial** | Race conditions, double-spend prevention, atomicity | `select_for_update` via concurrent requests |
| **Security** | SQL injection, XSS, unauthorized access, rate limits | OWASP ZAP (manual), `django.test` |
| **Performance** | Pagination, caching hit/miss, response times | `pytest-benchmark`, `locust` |

### 6.3 Test Fixtures (provided in `apps/conftest.py`)

| Fixture | Returns | Purpose |
|---|---|---|
| `api_client` | DRF `APIClient` | Unauthenticated requests |
| `user_data` | `dict` | Registration payload |
| `user` | `User` model | Authenticated user |
| `auth_client` | `APIClient` with JWT | Authenticated requests |
| `auth_headers` | `dict` | For `client.get(..., **headers)` |

### 6.4 Test Factories (provided in `apps/factories.py`)

| Factory | Creates |
|---|---|
| `UserFactory` | User with sequence email |
| `WalletFactory` | Wallet with $1,000 balance |
| `TransactionFactory` | Deposit transaction |
| `CryptoWalletFactory` | Crypto wallet with 1 BTC |
| `CryptoOrderFactory` | Pending crypto order |
| `CryptoHoldingFactory` | 0.5 BTC holding |
| `OrderFactory` | Pending stock order |
| `HoldingFactory` | 100 AAPL shares |
| `PortfolioFactory` | Portfolio with $50k cash |
| `MarketQuoteFactory` | AAPL at $175 |
| `NotificationFactory` | Order filled notification |
| `BankAccountFactory` | Virtual bank account |
| `BankCardFactory` | Active VISA card |

### 6.5 Example Test

```python
import pytest
from rest_framework import status
from wallet.models import Wallet


class TestWalletDeposit:
    def test_deposit_increases_balance(self, auth_client, user):
        initial = Wallet.objects.get(user=user).balance_cents
        response = auth_client.post("/api/v1/wallet/deposit/", {"amount_cents": 50000})
        assert response.status_code == status.HTTP_200_OK
        final = Wallet.objects.get(user=user).balance_cents
        assert final == initial + 50000

    def test_deposit_negative_amount_fails(self, auth_client):
        response = auth_client.post("/api/v1/wallet/deposit/", {"amount_cents": -100})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_deposit_requires_auth(self, api_client):
        response = api_client.post("/api/v1/wallet/deposit/", {"amount_cents": 50000})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

---

## 7. Production Deployment Checklist

### Pre-Deployment

- [ ] Environment variables configured (`.env` or AWS Secrets Manager)
- [ ] `SECRET_KEY` is strong, unique, and rotated
- [ ] `DEBUG=False` in production settings
- [ ] `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` set correctly
- [ ] Database migrations run (`python manage.py migrate`)
- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] Redis reachable and pingable
- [ ] Celery worker + beat running
- [ ] SSL certificates installed and auto-renewing
- [ ] Sentry DSN configured for error tracking

### Runtime Monitoring

- [ ] Health check endpoint (`/api/v1/health/`) monitored (15s interval)
- [ ] Database connection pool not exhausted (monitor `idle_in_transaction`)
- [ ] Redis memory usage < 70%
- [ ] Celery queue depth monitored (alert if > 1000 pending)
- [ ] API response times tracked (p99 < 500ms target)
- [ ] Error rates tracked (< 0.1% 5xx target)
- [ ] Rate limit counters not triggering false positives

### Scaling Triggers

| Metric | Threshold | Action |
|---|---|---|
| CPU > 70% | 5 min avg | Add Django/Gunicorn task |
| API latency p99 > 1s | 5 min avg | Add task, check DB queries |
| Celery queue depth > 1000 | sustained | Scale Celery workers |
| Redis memory > 70% | sustained | Scale Redis cluster shards |
| WebSocket connections > 40k | per instance | Add Gateway instance |

---

## 8. Error Codes

| HTTP | Code | Meaning |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Invalid input data |
| 401 | `AUTHENTICATION_FAILED` | Missing/expired/invalid JWT |
| 403 | `FORBIDDEN` | Not authorized for resource |
| 404 | `NOT_FOUND` | Resource does not exist |
| 409 | `INSUFFICIENT_FUNDS` | Not enough balance for operation |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error (check Sentry) |
| 501 | `NOT_IMPLEMENTED` | Feature not yet available (bill pay) |
| 503 | `SERVICE_UNAVAILABLE` | Health check failed (DB/Redis down) |

---

## 9. Quick Reference: All API Endpoints

| # | Method | Path | Module |
|---|---|---|---|
| 1 | GET | `/api/v1/health/` | Health |
| 2-8 | * | `/api/v1/auth/*` | Auth (7 endpoints) |
| 9-11 | * | `/api/v1/wallet/*` | Wallet (3) |
| 12-23 | * | `/api/v1/crypto/*` | Crypto (12) |
| 24-29 | * | `/api/v1/banking/*` | Banking (6) |
| 30-38 | * | `/api/v1/banking/cards/*` | Cards (9) |
| 39-40 | * | `/api/v1/kyc/*` | KYC (2) |
| 41-45 | * | `/api/v1/market/*` | Market Data (5) |
| 46-47 | * | `/api/v1/portfolio/*` | Portfolio (2) |
| 48-52 | * | `/api/v1/trading/*` | Trading (5) |
| 53-54 | * | `/api/v1/notifications/*` | Notifications (2) |
| 55-61 | * | `/api/v1/ai/*` | AI (7) |

**Total: 61 API endpoints**

---

*Last updated: July 2026 • Zigma Backend v2.0*
