import re

from rest_framework import serializers

from chain_wallet.models import ConnectedWallet


BASE58 = r"[1-9A-HJ-NP-Za-km-z]"


def is_valid_address(chain, address):
    if chain in (ConnectedWallet.Chain.ETHEREUM, ConnectedWallet.Chain.BNB, ConnectedWallet.Chain.POLYGON):
        return bool(re.fullmatch(r"0x[a-fA-F0-9]{40}", address))
    if chain == ConnectedWallet.Chain.BITCOIN:
        legacy = re.fullmatch(r"(?:[13]" + BASE58 + r"{25,34})", address)
        segwit = re.fullmatch(r"bc1[ac-hj-np-z02-9]{11,71}", address, re.IGNORECASE)
        return bool(legacy or segwit)
    if chain == ConnectedWallet.Chain.SOLANA:
        return bool(re.fullmatch(BASE58 + r"{32,44}", address))
    return False


class ConnectedWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectedWallet
        fields = ("id", "chain", "address", "label", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        chain = attrs.get("chain", getattr(self.instance, "chain", None))
        address = attrs.get("address", getattr(self.instance, "address", None))
        if chain and address and not is_valid_address(chain, address):
            raise serializers.ValidationError({"address": "Address format does not match the selected network."})
        return attrs

    def validate_address(self, value):
        return value.strip()
