# Generated by Django 4.1.12 on 2024-05-28 10:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_cartitem_special_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='specialproduct',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='specialproduct',
            name='unit',
        ),
        migrations.RemoveField(
            model_name='specialproduct',
            name='unit_price',
        ),
        migrations.AddField(
            model_name='specialproduct',
            name='units',
            field=models.ManyToManyField(blank=True, related_name='special_products', to='home.unit'),
        ),
        migrations.AddField(
            model_name='unit',
            name='special_product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='home.specialproduct'),
        ),
    ]
