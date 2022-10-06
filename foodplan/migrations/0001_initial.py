# Generated by Django 2.2.24 on 2022-10-06 18:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, upload_to='image')),
                ('calories', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DishType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Ingridients',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.CharField(max_length=200)),
                ('amount', models.IntegerField(blank=True, null=True)),
                ('dish', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foodplan.Dish')),
            ],
        ),
    ]