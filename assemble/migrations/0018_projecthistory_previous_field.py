# Generated by Django 3.0.3 on 2020-03-24 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assemble', '0017_auto_20200324_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='projecthistory',
            name='previous_field',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
