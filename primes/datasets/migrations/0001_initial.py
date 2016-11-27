# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-27 07:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upload', models.FileField(upload_to='')),
                ('input', models.TextField()),
                ('result', models.TextField()),
                ('status', models.NullBooleanField(default=None)),
                ('exception_message', models.CharField(max_length=255)),
                ('added', models.DateField(auto_now_add=True)),
                ('checked', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]