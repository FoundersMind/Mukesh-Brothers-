# Generated by Django 4.1.12 on 2024-06-30 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0029_bucket_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='bucket',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='bucket_images/'),
        ),
    ]
