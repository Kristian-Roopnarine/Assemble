# Generated by Django 3.0.3 on 2020-03-12 16:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assemble', '0005_auto_20200311_1445'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('description', models.TextField(max_length=400)),
                ('slug', models.SlugField(blank=True, max_length=100, null=True, unique=True)),
                ('complete', models.BooleanField(default=False)),
                ('user', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectComponentTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('description', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=100, null=True, unique=True)),
                ('completed', models.BooleanField(default=False)),
                ('task', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='component', to='assemble.ProjectComponentTest')),
            ],
        ),
    ]
