# Generated by Django 2.2.5 on 2020-02-06 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20200206_0135'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image2',
            field=models.ImageField(null=True, upload_to='pic_folder/'),
        ),
        migrations.AddField(
            model_name='product',
            name='image3',
            field=models.ImageField(null=True, upload_to='pic_folder/'),
        ),
        migrations.AddField(
            model_name='product',
            name='image4',
            field=models.ImageField(null=True, upload_to='pic_folder/'),
        ),
        migrations.AddField(
            model_name='product',
            name='image5',
            field=models.ImageField(null=True, upload_to='pic_folder/'),
        ),
        migrations.AddField(
            model_name='productrating',
            name='review',
            field=models.TextField(max_length=2000, null=True),
        ),
    ]
