# Generated by Django 5.0.6 on 2024-07-21 12:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0040_videorequest_video'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('billing_address', models.TextField()),
                ('city_town', models.CharField(max_length=50)),
                ('firm_name', models.CharField(blank=True, max_length=100)),
                ('postcode', models.CharField(max_length=20)),
                ('phone', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('gst_number', models.CharField(blank=True, max_length=50)),
                ('delivery_address', models.TextField(blank=True)),
                ('payment_method', models.CharField(choices=[('cash', 'Cash'), ('online', 'Online')], max_length=10)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('bucket_discount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('coupon_discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('final_total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.PositiveIntegerField()),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='home.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.product')),
            ],
        ),
    ]
