# Generated by Django 4.1.12 on 2024-07-19 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0035_appliedcoupon'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subproduct_id', models.IntegerField()),
                ('firm_name', models.CharField(max_length=255)),
                ('contact_no', models.CharField(max_length=20)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='AppliedCoupon',
        ),
    ]
