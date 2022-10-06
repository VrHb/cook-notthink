from django.db import models


class Dish(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='image', blank=True)
    calories = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.title}{self.description}{self.image}{self.calories}'


class Ingridients(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    product = models.CharField(max_length=200)
    amount = models.IntegerField(blank=True, null=True)


class DishType(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class User(models.Model):
    user_id = models.IntegerField(verbose_name='Telegram ID юзера')
    full_name = models.CharField(verbose_name='Полное имя', max_length=50)
    phonenumber = models.CharField(verbose_name='Номер телефона', max_length=30)

    def __str__(self):
        return self.full_name
