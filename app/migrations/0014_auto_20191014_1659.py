# Generated by Django 2.2.6 on 2019-10-14 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_auto_20191009_0836'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prediction',
            name='user',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='predictionbk',
            name='coefficient',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
    ]
