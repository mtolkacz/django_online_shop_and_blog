# Generated by Django 2.2.10 on 2020-05-30 10:48

import djmoney.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='price',
            field=djmoney.models.fields.MoneyField(decimal_places=2, default_currency='USD', editable=False, max_digits=14),
        ),
    ]
