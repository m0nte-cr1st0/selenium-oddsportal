# Generated by Django 2.2.6 on 2019-10-07 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prediction',
            name='date',
            field=models.CharField(max_length=254),
        ),
    ]
