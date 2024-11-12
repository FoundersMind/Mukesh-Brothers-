# Generated by Django 5.1 on 2024-10-08 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0044_product_qr_code_subproduct_qr_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total_quantity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='unit_quantity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]