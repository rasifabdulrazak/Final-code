# Generated by Django 4.0.1 on 2022-02-22 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0045_alter_order_placed_status_alter_wishlist_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order_placed',
            name='status',
            field=models.CharField(choices=[('On the way', 'On the way'), ('Delivered', 'Delivered'), ('Packed', 'Packed'), ('Accepted', 'Accepted')], default='placed', max_length=100),
        ),
        migrations.AlterField(
            model_name='wishlist',
            name='guest_user',
            field=models.CharField(max_length=300, null=True),
        ),
    ]
