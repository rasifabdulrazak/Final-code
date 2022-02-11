# Generated by Django 4.0.1 on 2022-02-02 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_products_offer_alter_order_placed_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='offer',
            new_name='category_offer',
        ),
        migrations.RenameField(
            model_name='products',
            old_name='offer',
            new_name='product_offer',
        ),
        migrations.AlterField(
            model_name='order_placed',
            name='status',
            field=models.CharField(choices=[('On the way', 'On the way'), ('Accepted', 'Accepted'), ('Canceled', 'Canceled'), ('Packed', 'Packed'), ('Return', 'Return'), ('Delivered', 'Delivered')], default='pending', max_length=100),
        ),
    ]
