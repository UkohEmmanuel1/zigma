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
        self.user = get_user_model().objects.create_user(email="wallet@example.com", password="test-password-123")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_user_can_register_public_address(self):
        response = self.client.post("/api/v1/chain-wallets/", {"chain": "ethereum", "address": "0x" + "a" * 40}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ConnectedWallet.objects.get().user, self.user)

    def test_invalid_address_is_rejected(self):
        response = self.client.post("/api/v1/chain-wallets/", {"chain": "ethereum", "address": "invalid"}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_wallets_are_scoped_to_authenticated_user(self):
        ConnectedWallet.objects.create(user=self.user, chain="ethereum", address="0x" + "b" * 40)
        response = self.client.get("/api/v1/chain-wallets/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
