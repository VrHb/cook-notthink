from django.db import models


class Dish(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='image', blank=True)
    calories = models.CharField(max_length=200, blank=True, null=True)
    dishtype = models.CharField(max_length=200, blank=True, null=True)
    ingridients = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.title}{self.description}{self.image}{self.calories}{self.dishtype}{self.ingridients}'


class User(models.Model):
    user_id = models.IntegerField(verbose_name='Telegram ID юзера')
    full_name = models.CharField(verbose_name='Полное имя', max_length=50)
    phonenumber = models.CharField(verbose_name='Номер телефона', max_length=30)

    def __str__(self):
        return self.full_name
