# Generated by Django 4.0.1 on 2022-02-04 04:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_alter_order_placed_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order_placed',
            name='status',
            field=models.CharField(choices=[('On the way', 'On the way'), ('Return', 'Return'), ('Packed', 'Packed'), ('Accepted', 'Accepted'), ('Delivered', 'Delivered'), ('Canceled', 'Canceled')], default='pending', max_length=100),
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coupen_code', models.CharField(max_length=6)),
                ('discount', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.order_placed')),
            ],
        ),
    ]
