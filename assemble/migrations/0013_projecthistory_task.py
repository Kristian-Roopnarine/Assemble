# Generated by Django 3.0.3 on 2020-03-21 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assemble', '0012_remove_projecthistory_task'),
    ]

    operations = [
        migrations.AddField(
            model_name='projecthistory',
            name='task',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]