# Generated by Django 5.0.4 on 2024-04-27 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0011_order_pstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending Review'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=10),
        ),
    ]
