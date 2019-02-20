# Generated by Django 2.1.4 on 2019-02-20 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diaries', '0005_auto_20190118_2007'),
    ]

    operations = [
        migrations.AddField(
            model_name='diary',
            name='comments_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='diary',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='diary',
            name='likes_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
