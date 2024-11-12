# Generated by Django 5.1 on 2024-10-14 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0048_subproduct_gst_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='price_before_gst',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]