# Generated by Django 5.1.4 on 2024-12-14 17:27

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linkagro', '0005_alter_perfilusuario_auth_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfilusuario',
            name='auth_token',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
