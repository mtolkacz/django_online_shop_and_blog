# Generated by Django 2.2.10 on 2020-06-29 01:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20200621_0100'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='thumbnail',
            field=models.ImageField(default='pic_folder/None/no-img.jpg', upload_to='pic_folder/'),
        ),
    ]
