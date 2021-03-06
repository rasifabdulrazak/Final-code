# Generated by Django 4.0.1 on 2022-02-22 04:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0044_alter_order_placed_status_alter_wishlist_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order_placed',
            name='status',
            field=models.CharField(choices=[('Delivered', 'Delivered'), ('Packed', 'Packed'), ('On the way', 'On the way'), ('Accepted', 'Accepted')], default='placed', max_length=100),
        ),
        migrations.AlterField(
            model_name='wishlist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
