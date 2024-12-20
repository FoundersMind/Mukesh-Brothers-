# Generated by Django 4.1.12 on 2024-05-25 16:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile_number', models.CharField(max_length=15, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('Category 1', 'Category 1'), ('Category 2', 'Category 2'), ('Category 3', 'Category 3')], max_length=100)),
                ('cost', models.DecimalField(decimal_places=3, max_digits=20)),
                ('quantity_available', models.DecimalField(decimal_places=3, max_digits=10)),
                ('unit', models.CharField(choices=[('grams', 'Grams'), ('kg', 'Kilograms')], default='grams', max_length=20)),
                ('image', models.ImageField(blank=True, null=True, upload_to='media/')),
                ('stock_date', models.DateField(auto_now_add=True)),
                ('last_sales_date', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('image', models.ImageField(blank=True, null=True, upload_to='product_images')),
            ],
        ),
        migrations.CreateModel(
            name='SpecialSaleProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('image', models.ImageField(blank=True, null=True, upload_to='product_images')),
            ],
        ),
        migrations.CreateModel(
            name='subproduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('image', models.ImageField(blank=True, null=True, upload_to='product_images')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='home.product')),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('unit', models.CharField(choices=[('10gm', '10 Grams'), ('50gm', '50 Grams'), ('100gm', '100 Grams'), ('250gm', '250 Grams'), ('500gm', '500 Grams'), ('1kg', '1 Kilogram'), ('10kg', '10 Kilogram'), ('50kg', '50 Kilogram'), ('100kg', '100 Kilogram')], max_length=20)),
                ('quantity', models.PositiveIntegerField(default=0, null=True)),
                ('Subproduct', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.subproduct')),
                ('special_product', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='home.specialsaleproduct')),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('unit_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.cart')),
                ('subproduct', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.subproduct')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.unit')),
            ],
        ),
        migrations.AddField(
            model_name='cart',
            name='items',
            field=models.ManyToManyField(through='home.CartItem', to='home.unit'),
        ),
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
