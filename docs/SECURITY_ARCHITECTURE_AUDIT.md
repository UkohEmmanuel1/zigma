# Zigma security and architecture audit

Branch: `feat/noncustodial-wallet-foundation`

## Scope reviewed

Repository tree, Django settings and URL routing, wallet and crypto services/views/models, trading service, requirements, environment template, and Supabase SQL migration inventory.

## Findings

### Critical — simulated fiat deposits credit balances

The legacy `POST /api/v1/wallet/deposit/` endpoint previously increased a user's fiat ledger balance directly from client-supplied input. It did not verify a payment-provider webhook or settlement.

**Mitigation in this branch:** endpoint now returns HTTP 503 with code `DEPOSITS_DISABLED_PENDING_VERIFIED_PROVIDER`. Do not re-enable until provider-side payment verification, idempotency, webhook signature validation, and reconciliation exist.

### High — simulated crypto execution

The crypto service contains hardcoded USD rates and random fallback rates. Crypto market orders and swaps also contain random pricing/execution behavior. These are not valid settlement or exchange integrations and must not be exposed as real-money functionality.

**Required mitigation:** keep these flows disabled in any user-facing production release until an exchange/liquidity provider or on-chain swap router, quote expiry, slippage controls, transaction receipts, and reconciliation are implemented and tested. The current branch does not yet rewrite every legacy trading route.

### High — custodial-style ledger is not a blockchain wallet

The existing `Wallet`, `CryptoWallet`, and `CryptoHolding` records are application-side ledgers. They do not represent on-chain keys or independently verified blockchain balances.

**Architecture decision:** Zigma's first wallet release is non-custodial. The new `ConnectedWallet` model stores only a user's public chain/address association. No private keys, seed phrases, or signing secrets are accepted or stored.

### Medium — address registration is not ownership verification

The new API validates basic address format and scopes records to the authenticated user. A user can currently register an address without proving control of it.

**Next step:** implement a short-lived nonce and EIP-191/EIP-4361-compatible signed-message challenge for EVM networks, plus chain-appropriate proof flows for Bitcoin and Solana. Verify signatures server-side and prevent nonce replay.

### Medium — market and trading integrations need source validation

The trading service uses the latest stored market quote. Production readiness requires source provenance, quote freshness thresholds, symbol mapping, outage handling, and execution confirmation. A cached quote alone is not an executable price.

## Implemented in this branch

- Added `chain_wallet` Django app and initial migration.
- Added authenticated list/create/delete API for connected public addresses.
- Added format checks for Ethereum, BNB Smart Chain, Polygon, Bitcoin, and Solana addresses.
- Scoped reads and deletes to the authenticated user.
- Added model uniqueness constraint for user + chain + address.
- Disabled the unsafe client-funded fiat deposit endpoint.
- Added initial address/API tests and project documentation.

## Verification status

The code has been committed to a feature branch. The repository connector does not execute the Django test suite, run migrations, or start the application. CI/local test results must be checked before merge. The tests are not represented as passing.

## Release gates

1. Run migrations and the new test suite against a disposable local database.
2. Review generated migration SQL and confirm it does not alter existing financial tables.
3. Disable legacy simulated buy/sell/order/swap endpoints from production routing until real execution is integrated.
4. Implement signed ownership verification and replay protection.
5. Integrate trusted RPC/indexer sources and verify balances/transactions on-chain.
6. Add transaction simulation, chain ID checks, gas estimation, fee display, and explicit wallet-side signing.
7. Add rate limiting, audit events, monitoring, dependency scanning, and security review.
8. Obtain jurisdiction-specific legal/compliance review before offering exchange, custody, fiat, or payment services.
