# Generated by Django 3.0.3 on 2020-03-24 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assemble', '0016_auto_20200323_2132'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projecthistory',
            name='after',
        ),
        migrations.RemoveField(
            model_name='projecthistory',
            name='before',
        ),
        migrations.AddField(
            model_name='projecthistory',
            name='status',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.DeleteModel(
            name='HistoricalProfile',
        ),
    ]
