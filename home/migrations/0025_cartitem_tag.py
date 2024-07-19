# Generated by Django 4.1.12 on 2024-06-10 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0024_cartitem_is_combo_bundle'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='tag',
            field=models.CharField(blank=True, choices=[('', 'None'), ('new', 'New'), ('best_seller', 'Best Seller'), ('combo_bundle', 'Combo/Bundle')], default='', max_length=20),
        ),
    ]
