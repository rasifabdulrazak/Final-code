# Generated by Django 4.0.1 on 2022-02-14 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0032_alter_order_placed_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order_placed',
            name='status',
            field=models.CharField(choices=[('Accepted', 'Accepted'), ('On the way', 'On the way'), ('Delivered', 'Delivered'), ('Packed', 'Packed')], default='placed', max_length=100),
        ),
    ]
