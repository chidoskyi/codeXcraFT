# Generated by Django 4.2.7 on 2023-11-02 02:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_product_registrated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='color',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='product',
            name='registrated',
            field=models.BooleanField(),
        ),
    ]
