# Generated by Django 5.0.4 on 2024-04-10 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0004_alter_product_ingredients'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='Description',
            field=models.TextField(blank=True, null=True),
        ),
    ]