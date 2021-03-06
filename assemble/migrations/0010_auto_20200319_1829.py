# Generated by Django 3.0.3 on 2020-03-19 22:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assemble', '0009_projecthistory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projecthistory',
            old_name='name',
            new_name='project',
        ),
        migrations.RemoveField(
            model_name='historicalprojectcomponent',
            name='description',
        ),
        migrations.RemoveField(
            model_name='projectcomponent',
            name='description',
        ),
        migrations.AddField(
            model_name='projecthistory',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='assemble.Profile'),
        ),
        migrations.AlterField(
            model_name='projecthistory',
            name='after',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='projecthistory',
            name='before',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
    ]
