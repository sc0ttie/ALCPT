# Generated by Django 3.1.1 on 2020-12-10 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alcpt', '0003_userachievement_unlock'),
    ]

    operations = [
        migrations.AddField(
            model_name='achievement',
            name='level',
            field=models.IntegerField(default=0),
        ),
    ]
