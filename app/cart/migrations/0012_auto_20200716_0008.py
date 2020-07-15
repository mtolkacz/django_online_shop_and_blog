# Generated by Django 2.2.10 on 2020-07-15 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0011_auto_20200605_2302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='createdate',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='updatedate',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='address_2',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='delivereddate',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='preparationdate',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='sentdate',
            field=models.DateTimeField(editable=False, null=True),
        ),
    ]
