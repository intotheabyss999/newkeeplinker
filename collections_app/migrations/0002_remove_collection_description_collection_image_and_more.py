# Generated by Django 5.1 on 2024-09-18 14:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collections_app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collection',
            name='description',
        ),
        migrations.AddField(
            model_name='collection',
            name='image',
            field=models.CharField(default='example2.svg', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='collection',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collections_from_app', to=settings.AUTH_USER_MODEL),
        ),
    ]
