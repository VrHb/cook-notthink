# Generated by Django 4.1.2 on 2022-10-07 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodplan', '0005_remove_ingridients_dish_dish_dishtype_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dish',
            name='calories',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
