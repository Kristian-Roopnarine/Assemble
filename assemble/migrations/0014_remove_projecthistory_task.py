# Generated by Django 3.0.3 on 2020-03-21 18:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assemble', '0013_projecthistory_task'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projecthistory',
            name='task',
        ),
    ]
