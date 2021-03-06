# Generated by Django 3.0.3 on 2020-03-19 21:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assemble', '0008_auto_20200316_2353'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('before', models.CharField(max_length=400)),
                ('after', models.CharField(max_length=400)),
                ('date_changed', models.DateTimeField(auto_now_add=True)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assemble.Project')),
            ],
        ),
    ]
