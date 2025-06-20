# Generated by Django 5.2.1 on 2025-06-17 03:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=50)),
                ('item_type', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, max_length=255, null=True)),
                ('give_date', models.DateTimeField(auto_now=True)),
                ('item_state', models.CharField(default='available', max_length=20)),
                ('give_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='give_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ItemImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_image', models.ImageField(blank=True, null=True, upload_to='item_image')),
                ('item_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gat_app.item')),
            ],
        ),
        migrations.CreateModel(
            name='ItemTaken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('take_date', models.DateTimeField(auto_now_add=True)),
                ('item_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gat_app.item')),
                ('take_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='take_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LogBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_action', models.CharField(max_length=20)),
                ('log_result', models.CharField(max_length=10)),
                ('log_date', models.DateTimeField(auto_now_add=True)),
                ('log_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='log_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('phone', models.IntegerField(unique=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
