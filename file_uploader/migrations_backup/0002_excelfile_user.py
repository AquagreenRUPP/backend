# Generated by Django 4.2.10 on 2025-03-22 15:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('file_uploader', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='excelfile',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='excel_files', to=settings.AUTH_USER_MODEL),
        ),
    ]
