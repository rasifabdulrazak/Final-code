# Generated by Django 4.0.1 on 2022-02-02 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_alter_category_category_offer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='category_offer',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='order_placed',
            name='status',
            field=models.CharField(choices=[('Delivered', 'Delivered'), ('Accepted', 'Accepted'), ('On the way', 'On the way'), ('Canceled', 'Canceled'), ('Packed', 'Packed'), ('Return', 'Return')], default='pending', max_length=100),
        ),
        migrations.AlterField(
            model_name='products',
            name='product_offer',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
