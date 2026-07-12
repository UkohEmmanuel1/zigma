# Zigma Backend Documentation

## Project Overview

Zigma Backend is an AI-powered paper trading platform API for stocks and crypto. It allows users to register, manage a virtual portfolio, place market/limit/stop orders, track market data, receive notifications, and interact with an AI trading assistant powered by Google Gemini.

---

## Tech Stack

| Component | Technology |
|---|---|
| **Framework** | Django 6.0, Django REST Framework |
| **Task Queue** | Celery with Redis broker |
| **Database** | PostgreSQL 16 (production) / SQLite (local dev) |
| **Market Data** | Alpaca Markets API (paper trading) |
| **AI** | Google Gemini 2.0 Flash |
| **Auth** | JWT (djangorestframework-simplejwt) |
| **Deployment** | Docker, Docker Compose, GitHub Actions |

---

## Architecture

```
zigma_backend/
├── app/                    # Django project config
│   ├── __init__.py
│   ├── asgi.py             # ASGI entry point
│   ├── urls.py             # Root URL routing
│   └── wsgi.py             # WSGI entry point
├── apps/
│   ├── ai_engine/          # AI chat & portfolio analysis
│   ├── market_data/        # Market quotes, price history, symbol search
│   ├── notifications/      # User alerts & notifications
│   ├── portfolio/          # Portfolio management & snapshots
│   ├── shared/             # Shared utilities (placeholder)
│   ├── trading/            # Order execution & trade management
│   ├── users/              # Authentication & user profiles
│   └── wallet/             # Digital wallet (placeholder)
├── zigma_core/             # Core settings & Celery config
│   ├── __init__.py         # Celery app import
│   ├── celery.py           # Celery application setup
│   └── settings/
│       ├── base.py         # Base settings (shared)
│       └── dev.py          # Development settings (used by default)
├── requirements/
│   └── base.txt            # Python dependencies
├── supabase/
│   └── migrations/         # Optional Supabase SQL migrations
│       ├── 0001_market_data.sql
│       ├── 0002_trading.sql
│       ├── 0003_notifications.sql
│       └── 0004_ai_chat.sql
├── supabase_schema.sql     # Optional Supabase users table
├── manage.py               # Django CLI entry point
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Multi-service orchestration
├── .env.example            # Environment variable template
├── .github/workflows/ci.yml
├── README.md
└── LICENSE
```

---

## Setup & Installation

### Prerequisites

- Python 3.12
- PostgreSQL 16 (production) or SQLite (local development)
- Redis 7 (for Celery task queue)

### Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | — | Django secret key (used for JWT signing) |
| `DEBUG` | `False` | Debug mode |
| `USE_LOCAL_DB` | `False` | `True` uses SQLite, `False` uses PostgreSQL |
| `DB_NAME` | `postgres` | PostgreSQL database name |
| `DB_USER` | `postgres` | PostgreSQL username |
| `DB_PASSWORD` | — | PostgreSQL password |
| `DB_HOST` | — | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Redis broker URL |
| `APCA_API_KEY_ID` | — | Alpaca Markets API key |
| `APCA_API_SECRET_KEY` | — | Alpaca Markets secret key |
| `APCA_BASE_URL` | `https://paper-api.alpaca.markets` | Alpaca API base URL |
| `GEMINI_API_KEY` | — | Google Gemini API key |

### Local Development

```bash
# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements\base.txt

# Run migrations
python manage.py migrate

# Start dev server
python manage.py runserver

# Start Celery worker (separate terminal)
celery -A zigma_core worker --loglevel=info
```

### Docker

```bash
docker-compose up --build
```

Starts PostgreSQL, Redis, Django API (port 8000), and Celery worker.

---

## Configuration

### Settings Files

- **`zigma_core/settings/base.py`** — Shared base settings (BASE_DIR, AUTH_USER_MODEL, Supabase config). Not used as the primary settings module.
- **`zigma_core/settings/dev.py`** — Default settings module (set via `DJANGO_SETTINGS_MODULE=zigma_core.settings.dev`). Contains all app, middleware, database, REST framework, JWT, Celery, Alpaca, and Gemini configuration.

### Installed Apps

- `users`, `wallet`, `trading`, `market_data`, `ai_engine`, `notifications`, `shared`, `portfolio`
- Third-party: `rest_framework`, `corsheaders`, `django_filters`, `drf_spectacular`, `django_extensions`

---

## Database

### Models Overview

#### Users (`apps/users/models.py`)

| Model | Fields | Notes |
|---|---|---|
| `User` | `id` (UUID), `email`, `password`, `is_active`, `is_staff`, `created_at`, `updated_at` | Custom user model using email as unique identifier (no username). Extends `AbstractBaseUser`. Table: `users` |

#### Market Data (`apps/market_data/models.py`)

| Model | Fields | Notes |
|---|---|---|
| `MarketQuote` | `id`, `symbol`, `bid`, `ask`, `last`, `volume`, `timestamp`, `created_at`, `updated_at` | Current market quotes. Table: `market_quotes`, unmanaged |
| `PriceHistory` | `id`, `symbol`, `interval`, `open`, `high`, `low`, `close`, `volume`, `timestamp`, `created_at` | OHLCV price history. Table: `price_history`, managed |
| `WatchedSymbol` | `id`, `symbol`, `is_active`, `created_at`, `updated_at` | Symbols being tracked. Table: `market_watched_symbols`, managed |

#### Trading (`apps/trading/models.py`)

| Model | Fields | Notes |
|---|---|---|
| `Order` | `id`, `user`, `symbol`, `side`, `order_type`, `quantity`, `price`, `stop_price`, `filled_quantity`, `status`, `created_at`, `updated_at` | Trade orders. Table: `trading_orders`, unmanaged |
| `Holding` | `id`, `user`, `symbol`, `quantity`, `avg_entry_price`, `created_at`, `updated_at` | User holdings. Table: `trading_holdings`, unmanaged. Unique: `(user, symbol)` |

#### Portfolio (`apps/portfolio/models.py`)

| Model | Fields | Notes |
|---|---|---|
| `Portfolio` | `id`, `user`, `cash_balance`, `created_at`, `updated_at` | One-to-one with User. Table: `portfolio` |
| `PortfolioHolding` | `id`, `portfolio`, `symbol`, `quantity`, `avg_entry_price`, `created_at`, `updated_at` | Portfolio-level holdings. Table: `portfolio_holdings`. Unique: `(portfolio, symbol)` |
| `PortfolioSnapshot` | `id`, `portfolio`, `total_value`, `cash_balance`, `snapshot_date`, `created_at` | Daily portfolio snapshots. Table: `portfolio_snapshots`. Unique: `(portfolio, snapshot_date)` |

#### Notifications (`apps/notifications/models.py`)

| Model | Fields | Notes |
|---|---|---|
| `Notification` | `id`, `user`, `type`, `title`, `message`, `related_object_type`, `related_object_id`, `is_read`, `created_at` | User notifications. Table: `notifications`, unmanaged |

#### AI Engine (`apps/ai_engine/models.py`)

| Model | Fields | Notes |
|---|---|---|
| `AIChatSession` | `id`, `user`, `title`, `created_at`, `updated_at` | Chat sessions. Table: `ai_chat_sessions`, unmanaged |
| `AIMessage` | `id`, `session`, `role`, `content`, `metadata`, `created_at` | Chat messages. Table: `ai_messages`, unmanaged |

#### Wallet (`apps/wallet/models.py`)

| Model | Fields | Notes |
|---|---|---|
| `Wallet` | `id`, `user`, `balance_cents`, `currency`, `created_at`, `updated_at` | One-to-one with User. Table: `wallets` |
| `Transaction` | `id`, `wallet`, `type`, `amount_cents`, `balance_after_cents`, `status`, `reference`, `description`, `metadata`, `created_at` | Immutable transaction log. Table: `transactions` |
| `P2PTransfer` | `id`, `sender`, `recipient`, `amount_cents`, `note`, `status`, `created_at` | P2P between Zigma users. Table: `p2p_transfers` |

#### Crypto (`apps/crypto/models.py`)

| Model | Fields | Notes |
|---|---|---|
| `CryptoWallet` | `id`, `user`, `currency`, `balance` (NUMERIC 38,18), `address`, `created_at`, `updated_at` | Per-currency balances. Unique: `(user, currency)`. Table: `crypto_wallets` |
| `CryptoOrder` | `id`, `user`, `symbol`, `side`, `order_type`, `quantity`, `price`, `filled_quantity`, `status`, `is_paper`, `created_at` | Crypto-specific orders. Table: `crypto_orders` |
| `CryptoHolding` | `id`, `user`, `symbol`, `quantity`, `avg_entry_price`, `created_at`, `updated_at` | Crypto positions. Unique: `(user, symbol)`. Table: `crypto_holdings` |
| `CryptoSwa` | `id`, `user`, `from_currency`, `to_currency`, `from_amount`, `to_amount`, `rate`, `status`, `is_paper`, `created_at` | Crypto-to-crypto swaps. Table: `crypto_swaps` |

#### Banking (`apps/banking/models.py`)

| Model | Fields | Notes |
|---|---|---|
| `BankAccount` | `id`, `user`, `account_number`, `routing_number`, `provider`, `provider_account_id`, `balance_cents`, `status`, `created_at` | Virtual bank accounts. Table: `bank_accounts` |
| `BankTransaction` | `id`, `account`, `type`, `amount_cents`, `balance_after_cents`, `description`, `reference`, `status`, `created_at` | Banking activity log. Table: `bank_transactions` |

#### Cards (`apps/cards/models.py`)

| Model | Fields | Notes |
|---|---|---|
| `BankCard` | `id`, `user`, `provider`, `provider_card_id`, `last4`, `expiry_month`, `expiry_year`, `brand`, `status`, `daily_limit_cents`, `monthly_limit_cents`, `online_enabled`, `atm_enabled`, `metadata`, `created_at` | Virtual debit cards. Table: `bank_cards` |

#### KYC (`apps/kyc/models.py`)

| Model | Fields | Notes |
|---|---|---|
| `KYCVerification` | `id`, `user`, `status`, `document_type`, `document_front_url`, `document_back_url`, `selfie_url`, `verification_provider`, `provider_reference`, `created_at`, `updated_at` | One-to-one with User. Table: `kyc_verifications` |

### Unmanaged Tables

Models with `managed = False` are managed by Supabase migrations rather than Django migrations. The SQL migrations are located in `supabase/migrations/`:

- `0001_market_data.sql` — `market_quotes`, `price_history` tables
- `0002_trading.sql` — `trading_orders`, `trading_holdings` tables
- `0003_notifications.sql` — `notifications` table
- `0004_ai_chat.sql` — `ai_chat_sessions`, `ai_messages` tables
- `0005_wallet.sql` — `wallets`, `transactions`, `p2p_transfers` tables
- `0006_crypto.sql` — `crypto_wallets`, `crypto_orders`, `crypto_holdings`, `crypto_swaps` tables
- `0007_banking.sql` — `bank_accounts`, `bank_transactions` tables
- `0008_cards.sql` — `bank_cards` table
- `0009_kyc.sql` — `kyc_verifications` table

All Supabase tables have Row Level Security (RLS) enabled with appropriate policies.

---

## API Reference

All endpoints are prefixed with `/api/v1/`.  
Authentication uses JWT Bearer tokens (`Authorization: Bearer <token>`) unless marked as public.

---

### 1. Authentication (`/api/v1/auth/`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register/` | No | Create account. Body: `{email, password, password2}` → `{user, access, refresh}` |
| `POST` | `/auth/login/` | No | Login. Body: `{email, password}` → `{access, refresh, user}` |
| `POST` | `/auth/token/refresh/` | No | Refresh access token. Body: `{refresh}` → `{access}` |
| `GET` | `/auth/me/` | Yes | Current user `{id, email}` |
| `POST` | `/auth/change-password/` | Yes | Change password. Body: `{old_password, new_password}` |
| `POST` | `/auth/forgot-password/` | No | Request reset token. Body: `{email}` |
| `POST` | `/auth/reset-password/` | No | Reset password. Body: `{token, new_password}` |

---

### 2. Wallet & Fiat (`/api/v1/wallet/`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/wallet/` | Yes | Fiat wallet balance & currency |
| `POST` | `/wallet/deposit/` | Yes | Simulated deposit. Body: `{amount_cents}` |
| `GET` | `/wallet/transactions/` | Yes | Paginated transaction history |

---

### 3. Trading — Stocks (`/api/v1/trading/`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/trading/orders/` | Yes | List orders (`?symbol=`, `?status=`) |
| `POST` | `/trading/orders/create/` | Yes | Place order. Body: `{symbol, side, order_type, quantity, price?, stop_price?}` |
| `GET` | `/trading/orders/{id}/` | Yes | Get single order details |
| `POST` | `/trading/orders/{id}/cancel/` | Yes | Cancel a pending order |
| `GET` | `/trading/holdings/` | Yes | Current stock positions |

**Order types:** `market`, `limit`, `stop`  
**Side:** `buy`, `sell`

---

### 4. Crypto (`/api/v1/crypto/`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/crypto/wallets/` | Yes | List crypto wallet balances |
| `GET` | `/crypto/orders/` | Yes | List crypto orders (`?status=`) |
| `POST` | `/crypto/orders/create/` | Yes | Place crypto order. Body: `{symbol, side, order_type, quantity, price?, is_paper}` |
| `GET` | `/crypto/orders/{id}/` | Yes | Get order details |
| `POST` | `/crypto/orders/{id}/cancel/` | Yes | Cancel a pending order |
| `GET` | `/crypto/holdings/` | Yes | Current crypto positions |
| `GET` | `/crypto/swaps/` | Yes | List swap orders |
| `POST` | `/crypto/swaps/create/` | Yes | Swap crypto. Body: `{from_currency, to_currency, from_amount, is_paper}` |
| `GET` | `/crypto/swaps/{id}/` | Yes | Get swap details |
| `POST` | `/crypto/swaps/{id}/cancel/` | Yes | Cancel a pending swap |

**Order types:** `MARKET`, `LIMIT`  
**Side:** `BUY`, `SELL`

---

### 5. Market Data (`/api/v1/market/`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/market/quote/{symbol}/` | Public | Latest price quote |
| `GET` | `/market/quote/{market_type}/{symbol}/` | Public | Latest price by market type (STOCK/CRYPTO) |
| `GET` | `/market/candles/{symbol}/` | Public | OHLCV history (`?interval=`, `?start=`, `?end=`, `?limit=`) |
| `GET` | `/market/candles/{market_type}/{symbol}/` | Public | OHLCV history by market type |
| `GET` | `/market/search/` | Public | Search symbols (`?q=`) |

---

### 6. Banking (`/api/v1/banking/`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/banking/account/` | Yes | Open virtual bank account |
| `GET` | `/banking/account/detail/` | Yes | Account details (masked number, balance) |
| `GET` | `/banking/transactions/` | Yes | Bank transaction history |
| `POST` | `/banking/transfer/` | Yes | External bank transfer. Body: `{amount_cents, recipient_account_number, recipient_routing, note?}` |
| `POST` | `/banking/p2p/` | Yes | P2P to another user. Body: `{recipient_email, amount_cents, note?}` |
| `POST` | `/banking/billpay/` | Yes | Pay a bill (stub — returns 501) |

---

### 7. Virtual Debit Cards (`/api/v1/banking/cards/`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/banking/cards/` | Yes | List all cards (last4, expiry, brand, status, limits) |
| `POST` | `/banking/cards/create/` | Yes | Issue new virtual card. Body: `{brand?}` (VISA/MASTERCARD) |
| `GET` | `/banking/cards/{id}/` | Yes | Get single card details |
| `POST` | `/banking/cards/{id}/freeze/` | Yes | Freeze card |
| `POST` | `/banking/cards/{id}/unfreeze/` | Yes | Unfreeze card |
| `POST` | `/banking/cards/{id}/limits/` | Yes | Update limits. Body: `{daily_limit_cents?, monthly_limit_cents?}` |
| `POST` | `/banking/cards/{id}/toggle/online/` | Yes | Enable/disable online. Body: `{enabled}` |
| `POST` | `/banking/cards/{id}/toggle/atm/` | Yes | Enable/disable ATM. Body: `{enabled}` |
| `POST` | `/banking/cards/{id}/cancel/` | Yes | Permanently cancel card |

---

### 8. Portfolio (`/api/v1/portfolio/`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/portfolio/` | Yes | Portfolio overview with holdings, current prices, P&L |
| `GET` | `/portfolio/performance/` | Yes | Snapshot history (`?start_date=`, `?end_date=`) |

---

### 9. AI Assistant (`/api/v1/ai/`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/ai/chat/sessions/` | Yes | List chat sessions |
| `POST` | `/ai/chat/sessions/create/` | Yes | Create new session |
| `GET` | `/ai/chat/sessions/{id}/` | Yes | Get session details |
| `GET` | `/ai/chat/sessions/{id}/messages/` | Yes | Get message history |
| `POST` | `/ai/chat/sessions/{id}/messages/create/` | Yes | Send message. Body: `{content}` → AI reply |
| `POST` | `/ai/portfolio/analyze/` | Yes | Trigger AI portfolio analysis |
| `GET` | `/ai/stock/insight/{market_type}/{symbol}/` | Public | AI-generated stock/crypto insight |

---

### 10. Notifications (`/api/v1/notifications/`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/notifications/` | Yes | List notifications (`?unread_only=true`) |
| `POST` | `/notifications/mark-read/` | Yes | Mark as read. Body: `{ids: [...]}` or `{all: true}` → `{marked_read: count}` |

---

### 11. KYC (`/api/v1/kyc/`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/kyc/upload/` | Yes | Upload KYC documents. Body: `{document_type, document_front_url, document_back_url?, selfie_url?}` |
| `GET` | `/kyc/status/` | Yes | Get verification status |

---

**Real-time events** (prices, order status, AI streaming) are delivered via WebSocket through the Real-time Gateway at `wss://rt.zigma.io` (separate service, not part of this Django API).

---

## Authentication

### JWT Configuration

| Setting | Value |
|---|---|
| **Access token lifetime** | 1 hour |
| **Refresh token lifetime** | 7 days |
| **Algorithm** | HS256 (signed with Django's `SECRET_KEY`) |
| **Auth header** | `Authorization: Bearer <token>` |

### Auth Flow

```
Client                          Django API
  │                                │
  ├── POST /api/v1/auth/register/  │  Create user, return JWT
  ├── POST /api/v1/auth/login/     │  Verify credentials, return JWT
  ├── POST /api/v1/auth/token/refresh/  │  Refresh access token
  ├── GET  /api/v1/auth/me/        │  Return current user (Bearer token)
  ├── POST /api/v1/auth/change-password/ │  Update password (authenticated)
  ├── POST /api/v1/auth/forgot-password/ │  Generate reset token
  └── POST /api/v1/auth/reset-password/  │  Reset password with token
```

---

## Celery Tasks

### Beat Schedule

| Task | Schedule | Description |
|---|---|---|
| `market_data.tasks.fetch_market_data` | Every 30s | Fetch latest quotes for watched symbols from Alpaca |
| `market_data.tasks.fetch_price_history` | Every 5min | Fetch latest OHLCV bars for watched symbols |
| `portfolio.tasks.take_portfolio_snapshots` | Daily | Record daily portfolio snapshots |
| `trading.tasks.match_limit_orders` | Every 10s | Match pending limit/stop orders against current prices |

### Task Descriptions

- **`fetch_market_data`** — Queries all active `WatchedSymbol` entries and fetches latest quotes from Alpaca. Upserts into `MarketQuote`.
- **`fetch_price_history`** — Fetches latest 1-minute bars for watched symbols. Upserts into `PriceHistory`.
- **`take_portfolio_snapshots`** — For each portfolio, calculates total holdings value using latest quotes and creates a `PortfolioSnapshot` for the current date.
- **`match_limit_orders`** — Iterates pending limit/stop orders, checks current price against order conditions, and executes matching orders.

---

## Services

### Trading (`apps/trading/services.py`)

- **`place_order(user, symbol, side, order_type, quantity, price, stop_price)`** — Creates an order record. For market orders, immediately attempts execution.
- **`execute_market_order(order, fill_price)`** — Fills a market order: updates cash balance, creates/updates holdings (both `Holding` and `PortfolioHolding`). Generates notifications on fill/rejection.
- **`get_current_price(symbol)`** — Gets the latest price from `MarketQuote`.

### AI Engine (`apps/ai_engine/services.py`)

- **`get_gemini_client()`** — Initializes the Google Gemini 2.0 Flash model client.
- **`build_portfolio_context(user)`** — Builds a text summary of the user's portfolio (cash balance, holdings with current prices/P&L, recent orders).
- **`call_gemini(system_prompt, user_message, context)`** — Sends a prompt to Gemini and returns the AI response.
- **`generate_portfolio_analysis(user)`** — Generates a full portfolio analysis using a dedicated analysis prompt.

### Notifications (`apps/notifications/services.py`)

- **`create_notification(user, type, title, message, related_object_type, related_object_id)`** — Creates a notification record. Supported types: `order_filled`, `order_rejected`, `order_cancelled`.

---

## Deployment

### Docker

The `Dockerfile` uses `python:3.12-slim` with `psycopg2-binary` dependencies.

`docker-compose.yml` runs four services:
- **db** — PostgreSQL 16 Alpine
- **redis** — Redis 7 Alpine
- **web** — Django dev server on port 8000
- **celery** — Celery worker

### CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on push to `main`/`develop` and PRs to `main`:
- Sets up PostgreSQL 16 + Redis 7
- Installs Python dependencies
- Runs migrations
- Runs tests

---

## License

See `LICENSE` file for details.
