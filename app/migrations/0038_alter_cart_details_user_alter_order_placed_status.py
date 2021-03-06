# Generated by Django 4.0.1 on 2022-02-15 14:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0037_alter_cart_details_guest_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart_details',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='order_placed',
            name='status',
            field=models.CharField(choices=[('Delivered', 'Delivered'), ('On the way', 'On the way'), ('Accepted', 'Accepted'), ('Packed', 'Packed')], default='placed', max_length=100),
        ),
    ]
