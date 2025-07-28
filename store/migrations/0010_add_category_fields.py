# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_remove_cart_tax_remove_order_service_fee_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='icon',
            field=models.CharField(blank=True, help_text='Font Awesome icon class', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='is_featured',
            field=models.BooleanField(default=False, help_text='Whether to feature this category on the homepage'),
        ),
        migrations.AddField(
            model_name='category',
            name='order',
            field=models.IntegerField(default=0, help_text='Order in which to display this category'),
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['order', 'title'], 'verbose_name_plural': 'Categories'},
        ),
    ]