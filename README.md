# Zigma

Zigma is a crypto intelligence platform with a non-custodial, multi-chain wallet experience.

## Wallet security model

Zigma stores **public wallet addresses only**. It never asks for, receives, or stores private keys, seed phrases, recovery phrases, or signing secrets. Users retain control of their wallets and approve transactions in their wallet provider.

The first connected-address API supports Ethereum, BNB Smart Chain, Polygon, Bitcoin, and Solana address formats. Address registration is not proof of ownership; signed-message verification is a separate feature planned for a later milestone.

## Backend

- Django and Django REST Framework
- PostgreSQL (including Supabase-hosted PostgreSQL)
- Celery and Redis for background processing
- Docker-based development and production configuration

## Connected wallet API

All endpoints require the existing bearer-token authentication.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/chain-wallets/` | List the authenticated user's connected public addresses |
| POST | `/api/v1/chain-wallets/` | Register a public address |
| DELETE | `/api/v1/chain-wallets/{id}/` | Remove one of the authenticated user's addresses |

Example request:

```json
{
  "chain": "ethereum",
  "address": "0x0000000000000000000000000000000000000000",
  "label": "Main wallet"
}
```

Allowed `chain` values: `ethereum`, `bnb`, `polygon`, `bitcoin`, `solana`.

The API performs format validation only. It does not prove control of an address, check balances, or broadcast transactions. Never submit secrets or signing material to this API.

## Local development

1. Create and activate a Python virtual environment.
2. Install dependencies from `requirements/base.txt`.
3. Configure the environment using `.env.example`.
4. Set `DJANGO_SETTINGS_MODULE=zigma_core.settings.dev`.
5. Run `python manage.py migrate`.
6. Run `python manage.py test chain_wallet`.
7. Start the server with `python manage.py runserver`.

Use a local database for isolated development where possible. Do not run experimental migrations against production Supabase without reviewing and applying a backup/rollback plan.

## Current scope

The connected-address registry is the first non-custodial foundation. WalletConnect/Reown connection handshakes, signed-message ownership verification, chain RPC balance reads, transaction simulation, and user-approved transaction broadcasting are not yet implemented.
