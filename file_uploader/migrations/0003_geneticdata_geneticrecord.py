# Generated by Django 5.0.6 on 2025-06-06 16:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('file_uploader', '0002_cropimage_csv_file'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneticData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='genetic_data/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('file_type', models.CharField(choices=[('csv', 'CSV'), ('xlsx', 'Excel')], max_length=10)),
                ('total_records', models.IntegerField(default=0)),
                ('processed', models.BooleanField(default=False)),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GeneticRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_number', models.IntegerField()),
                ('location', models.CharField(max_length=100)),
                ('f5_fruit_number', models.CharField(max_length=50)),
                ('f5_code', models.CharField(max_length=50)),
                ('f6_full_name', models.CharField(max_length=200)),
                ('sixth_code', models.CharField(max_length=50)),
                ('fruit_number', models.CharField(max_length=50)),
                ('pollination_date', models.DateField(null=True)),
                ('harvest_date', models.DateField(null=True)),
                ('pedicel_length', models.FloatField(null=True)),
                ('pedicel_width', models.FloatField(null=True)),
                ('insertion_peduncle_size', models.FloatField(null=True)),
                ('fruit_weight', models.FloatField(null=True)),
                ('fruit_length', models.FloatField(null=True)),
                ('fruit_width', models.FloatField(null=True)),
                ('rind_thickness', models.FloatField(null=True)),
                ('rind_hardness', models.FloatField(null=True)),
                ('apex_size', models.FloatField(null=True)),
                ('rind_stripe', models.CharField(max_length=100, null=True)),
                ('flesh_hardness', models.CharField(max_length=100, null=True)),
                ('flesh_color', models.CharField(max_length=100, null=True)),
                ('brix_content', models.FloatField(null=True)),
                ('seeds_quantity', models.IntegerField(null=True)),
                ('remained_seeds', models.IntegerField(null=True)),
                ('genetic_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='records', to='file_uploader.geneticdata')),
                ('image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='genetic_records', to='file_uploader.cropimage')),
            ],
            options={
                'unique_together': {('genetic_data', 'record_number', 'f5_code')},
            },
        ),
    ]
