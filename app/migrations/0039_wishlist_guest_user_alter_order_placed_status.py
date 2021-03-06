# Generated by Django 4.0.1 on 2022-02-15 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0038_alter_cart_details_user_alter_order_placed_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='wishlist',
            name='guest_user',
            field=models.CharField(default='', max_length=300),
        ),
        migrations.AlterField(
            model_name='order_placed',
            name='status',
            field=models.CharField(choices=[('On the way', 'On the way'), ('Packed', 'Packed'), ('Delivered', 'Delivered'), ('Accepted', 'Accepted')], default='placed', max_length=100),
        ),
    ]
