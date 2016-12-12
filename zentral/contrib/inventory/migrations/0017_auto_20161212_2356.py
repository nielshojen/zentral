# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-12 23:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0016_auto_20161212_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessunit',
            name='mt_hash',
            field=models.CharField(max_length=40, unique=True),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='mt_hash',
            field=models.CharField(max_length=40, unique=True),
        ),
        migrations.AlterField(
            model_name='debpackage',
            name='mt_hash',
            field=models.CharField(max_length=40, unique=True),
        ),
        migrations.AlterField(
            model_name='link',
            name='mt_hash',
            field=models.CharField(max_length=40, unique=True),
        ),
        migrations.AlterField(
            model_name='machine',
            name='mt_hash',
            field=models.CharField(max_length=40, unique=True),
        ),
        migrations.AlterField(
            model_name='machinegroup',
            name='mt_hash',
            field=models.CharField(max_length=40, unique=True),
        ),
        migrations.AlterField(
            model_name='machinesnapshot',
            name='mt_hash',
            field=models.CharField(max_length=40, unique=True),
        ),
        migrations.AlterField(
            model_name='networkinterface',
            name='mt_hash',
            field=models.CharField(max_length=40, unique=True),
        ),
        migrations.AlterField(
            model_name='osversion',
            name='mt_hash',
            field=models.CharField(max_length=40, unique=True),
        ),
        migrations.AlterField(
            model_name='osxapp',
            name='mt_hash',
            field=models.CharField(max_length=40, unique=True),
        ),
        migrations.AlterField(
            model_name='osxappinstance',
            name='mt_hash',
            field=models.CharField(max_length=40, unique=True),
        ),
        migrations.AlterField(
            model_name='source',
            name='mt_hash',
            field=models.CharField(max_length=40, unique=True),
        ),
        migrations.AlterField(
            model_name='systeminfo',
            name='mt_hash',
            field=models.CharField(max_length=40, unique=True),
        ),
        migrations.AlterField(
            model_name='teamviewer',
            name='mt_hash',
            field=models.CharField(max_length=40, unique=True),
        ),
    ]
