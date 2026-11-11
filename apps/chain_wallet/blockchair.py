"""Read-only Blockchair adapter for supported chains.

Private keys and transaction signing must remain in the user's wallet client.
This module only retrieves public blockchain data.
"""
from urllib.parse import quote

import requests
from django.conf import settings


class BlockchairError(Exception):
    """Base exception for Blockchair provider failures."""


class UnsupportedBlockchairChain(BlockchairError):
    """Raised when Blockchair does not support the requested chain."""


class BlockchairUnavailable(BlockchairError):
    """Raised when Blockchair cannot provide a valid response."""


BLOCKCHAIR_CHAINS = {
    "bitcoin": "bitcoin",
    "ethereum": "ethereum",
}


def get_address_dashboard(chain: str, address: str) -> dict:
    """Fetch a public address dashboard for a supported chain."""
    chain_slug = BLOCKCHAIR_CHAINS.get(chain)
    if not chain_slug:
        raise UnsupportedBlockchairChain(
            f"Blockchair does not support the '{chain}' network. "
            "Use the configured RPC provider for this network."
        )

    encoded_address = quote(address, safe="")
    url = f"https://api.blockchair.com/{chain_slug}/dashboards/address/{encoded_address}"
    params = {"limit": 20}
    api_key = getattr(settings, "BLOCKCHAIR_API_KEY", "")
    if api_key:
        params["key"] = api_key
    if chain == "ethereum":
        params["transactions_instead_of_calls"] = "true"

    try:
        response = requests.get(url, params=params, timeout=12)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise BlockchairUnavailable("Blockchain data provider is temporarily unavailable.") from exc

    context = payload.get("context") or {}
    if context.get("code") not in (None, 200):
        raise BlockchairUnavailable("Blockchain data provider returned an error.")

    data = payload.get("data") or {}
    dashboard = data.get(address)
    if dashboard is None and len(data) == 1:
        dashboard = next(iter(data.values()))
    if not isinstance(dashboard, dict):
        raise BlockchairUnavailable("Blockchain provider returned an unexpected response.")

    return {
        "provider": "blockchair",
        "chain": chain,
        "address": address,
        "dashboard": dashboard,
        "context": context,
    }
