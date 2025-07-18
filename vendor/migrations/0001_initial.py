# Generated by Django 5.2.4 on 2025-07-07 12:09

import django.db.models.deletion
import shortuuid.django_fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('store', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('New Order', 'New Order'), ('Item Shipped', 'Item Shipped'), ('Item Delivered', 'Item Delivered')], default='New Order', max_length=100)),
                ('seen', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.orderitem')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vendor_notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Notifications',
            },
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, default='shop-image.jpg', upload_to='images')),
                ('store_name', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('vendor_id', shortuuid.django_fields.ShortUUIDField(alphabet='1234567890', length=6, max_length=20, prefix='', unique=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('slug', models.SlugField(blank=True, null=True)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vendor', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('payout_id', shortuuid.django_fields.ShortUUIDField(alphabet='1234567890', length=6, max_length=10, prefix='', unique=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('item', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='item', to='store.orderitem')),
                ('vendor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='vendor.vendor')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_type', models.CharField(blank=True, choices=[('PayPal', 'PayPal'), ('Stripe', 'Stripe'), ('Nigerian Bank Account', 'Nigerian Bank Account'), ('Indian Bank Account', 'Indian Bank Account'), ('USA Bank Account', 'USA Bank Account')], max_length=50, null=True)),
                ('country', models.CharField(choices=[('NG', 'Nigeria'), ('GH', 'Ghana'), ('CI', "Côte d'Ivoire"), ('SN', 'Senegal'), ('BJ', 'Benin'), ('TG', 'Togo'), ('GM', 'Gambia'), ('GN', 'Guinea'), ('LR', 'Liberia'), ('SL', 'Sierra Leone'), ('GLOBAL', 'Other / Global')], default='NG', help_text='Vendor’s country for bank account verification', max_length=16)),
                ('currency', models.CharField(blank=True, max_length=10, null=True)),
                ('bank_name', models.CharField(max_length=255)),
                ('bank_code', models.CharField(blank=True, max_length=50, null=True)),
                ('branch_code', models.CharField(blank=True, max_length=50, null=True)),
                ('account_number', models.CharField(max_length=50)),
                ('account_name', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('flutterwave_subaccount_id', models.CharField(blank=True, max_length=100, null=True)),
                ('split_value', models.PositiveIntegerField(blank=True, default=1, null=True)),
                ('stripe_id', models.CharField(blank=True, max_length=100, null=True)),
                ('paypal_address', models.CharField(blank=True, max_length=100, null=True)),
                ('vendor', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='vendor.vendor')),
            ],
            options={
                'verbose_name_plural': 'Bank Accounts',
            },
        ),
    ]
