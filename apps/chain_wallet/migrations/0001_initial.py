import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="ConnectedWallet",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("chain", models.CharField(choices=[("ethereum", "Ethereum"), ("bnb", "BNB Smart Chain"), ("polygon", "Polygon"), ("bitcoin", "Bitcoin"), ("solana", "Solana")], max_length=16)),
                ("address", models.CharField(max_length=128)),
                ("label", models.CharField(blank=True, max_length=40)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="connected_wallets", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "connected_wallets", "ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(model_name="connectedwallet", constraint=models.UniqueConstraint(fields=("user", "chain", "address"), name="uniq_user_chain_address")),
        migrations.AddIndex(model_name="connectedwallet", index=models.Index(fields=["chain", "address"], name="connected__chain_a2b6a4_idx")),
    ]
