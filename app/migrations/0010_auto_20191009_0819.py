# Generated by Django 2.2.6 on 2019-10-09 08:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20191009_0754'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='prediction',
            options={'ordering': ['-date']},
        ),
    ]
