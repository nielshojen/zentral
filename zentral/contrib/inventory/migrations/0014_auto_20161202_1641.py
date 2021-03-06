# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-02 16:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0013_auto_20161026_1328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machinesnapshot',
            name='type',
            field=models.CharField(blank=True, choices=[('DESKTOP', 'Desktop'), ('LAPTOP', 'Laptop'), ('MOBILE', 'Mobile'), ('SERVER', 'Server'), ('TABLET', 'Tablet'), ('VM', 'Virtual machine')], max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='networkinterface',
            name='mac',
            field=models.CharField(max_length=23),
        ),
    ]
