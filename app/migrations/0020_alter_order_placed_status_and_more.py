# Generated by Django 4.0.1 on 2022-02-04 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_alter_category_category_offer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order_placed',
            name='status',
            field=models.CharField(choices=[('On the way', 'On the way'), ('Return', 'Return'), ('Delivered', 'Delivered'), ('Accepted', 'Accepted'), ('Canceled', 'Canceled'), ('Packed', 'Packed')], default='pending', max_length=100),
        ),
        migrations.AlterField(
            model_name='products',
            name='discounted_price',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='products',
            name='selling_price',
            field=models.IntegerField(),
        ),
    ]
