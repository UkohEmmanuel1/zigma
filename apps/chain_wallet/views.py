from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from chain_wallet.blockchair import (
    BlockchairUnavailable,
    UnsupportedBlockchairChain,
    get_address_dashboard,
)
from chain_wallet.models import ConnectedWallet
from chain_wallet.serializers import ConnectedWalletSerializer


class ConnectedWalletListCreateView(generics.ListCreateAPIView):
    serializer_class = ConnectedWalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ConnectedWallet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ConnectedWalletDeleteView(generics.DestroyAPIView):
    serializer_class = ConnectedWalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ConnectedWallet.objects.filter(user=self.request.user)


class ConnectedWalletActivityView(APIView):
    """Return public on-chain address activity; never accesses signing material."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            wallet = ConnectedWallet.objects.get(pk=pk, user=request.user)
        except ConnectedWallet.DoesNotExist:
            return Response(
                {"detail": "Connected wallet not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            data = get_address_dashboard(wallet.chain, wallet.address)
        except UnsupportedBlockchairChain as exc:
            return Response(
                {
                    "error": "UNSUPPORTED_PROVIDER_CHAIN",
                    "detail": str(exc),
                    "chain": wallet.chain,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except BlockchairUnavailable:
            return Response(
                {
                    "error": "BLOCKCHAIN_PROVIDER_UNAVAILABLE",
                    "detail": "Could not retrieve blockchain activity. Please retry.",
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(data, status=status.HTTP_200_OK)
