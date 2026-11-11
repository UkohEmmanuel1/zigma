from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

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
