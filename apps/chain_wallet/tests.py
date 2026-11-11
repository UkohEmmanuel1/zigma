from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from chain_wallet.models import ConnectedWallet
from chain_wallet.serializers import is_valid_address


class WalletAddressValidationTests(TestCase):
    def test_evm_address_format(self):
        self.assertTrue(is_valid_address("ethereum", "0x" + "a" * 40))
        self.assertFalse(is_valid_address("ethereum", "0x123"))

    def test_bitcoin_address_format(self):
        self.assertTrue(is_valid_address("bitcoin", "1BoatSLRHtKNngkdXEeobR76b53LETtpyT"))
        self.assertFalse(is_valid_address("bitcoin", "not-a-bitcoin-address"))

    def test_solana_address_format(self):
        self.assertTrue(is_valid_address("solana", "11111111111111111111111111111111"))
        self.assertFalse(is_valid_address("solana", "0OIl"))


class ConnectedWalletAPITests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="wallet@example.com",
            password="test-password-123",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_user_can_register_public_address(self):
        response = self.client.post(
            "/api/v1/chain-wallets/",
            {"chain": "ethereum", "address": "0x" + "a" * 40},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ConnectedWallet.objects.get().user, self.user)

    def test_invalid_address_is_rejected(self):
        response = self.client.post(
            "/api/v1/chain-wallets/",
            {"chain": "ethereum", "address": "invalid"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_wallets_are_scoped_to_authenticated_user(self):
        ConnectedWallet.objects.create(
            user=self.user,
            chain="ethereum",
            address="0x" + "b" * 40,
        )
        response = self.client.get("/api/v1/chain-wallets/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    @patch("chain_wallet.blockchair.requests.get")
    def test_bitcoin_activity_uses_blockchair(self, mock_get):
        wallet = ConnectedWallet.objects.create(
            user=self.user,
            chain="bitcoin",
            address="1BoatSLRHtKNngkdXEeobR76b53LETtpyT",
        )
        provider_response = Mock()
        provider_response.json.return_value = {
            "context": {"code": 200},
            "data": {
                wallet.address: {
                    "address": {"balance": 125000},
                    "transactions": [],
                }
            },
        }
        provider_response.raise_for_status.return_value = None
        mock_get.return_value = provider_response

        response = self.client.get(f"/api/v1/chain-wallets/{wallet.id}/activity/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["provider"], "blockchair")
        self.assertEqual(response.data["dashboard"]["address"]["balance"], 125000)
        mock_get.assert_called_once()

    def test_activity_does_not_expose_another_users_wallet(self):
        other_user = get_user_model().objects.create_user(
            email="other@example.com",
            password="test-password-123",
        )
        wallet = ConnectedWallet.objects.create(
            user=other_user,
            chain="bitcoin",
            address="1BoatSLRHtKNngkdXEeobR76b53LETtpyT",
        )

        response = self.client.get(f"/api/v1/chain-wallets/{wallet.id}/activity/")

        self.assertEqual(response.status_code, 404)

    def test_unsupported_blockchair_chain_returns_clear_error(self):
        wallet = ConnectedWallet.objects.create(
            user=self.user,
            chain="solana",
            address="11111111111111111111111111111111",
        )

        response = self.client.get(f"/api/v1/chain-wallets/{wallet.id}/activity/")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "UNSUPPORTED_PROVIDER_CHAIN")
