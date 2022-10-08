import requests
import collections
from django.core.management.base import BaseCommand
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from foodplan.models import *
from pathvalidate import sanitize_filename
collections.Callable = collections.abc.Callable

class Command(BaseCommand):
    help = 'Парсер рецептов'

    def handle(self, *args, **options):
        pages = 4
        types = ("Вегетарианская","Безглютеновая","Мясные блюда")
        urls = (
                "https://www.iamcook.ru/event/everyday/everyday-vegetarian",
                "https://www.iamcook.ru/event/baking/gluten-free-baking",
                "https://www.iamcook.ru/showsubsection/myasnie_bluda",
        )
        for url in urls:
            for dish_type in types:
                for page in range(1, pages+1):
                    recipes_url = f"{url}/{page}"
                    response = requests.get(recipes_url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    titles_soup = soup.find_all("div", class_="header")
                    titles = [title.text for title in titles_soup]
                    descriptions_soup = soup.find_all("div", class_="description")
                    descriptions = [sanitize_filename(description.text) for description in descriptions_soup]
                    ingredients_soup = soup.find_all("div", class_="ingredients")
                    ingredients = [(ingredient.text).replace("\n", " ") for ingredient in ingredients_soup]
                    imgs_url_soup = soup.find_all("img", {"itemprop": "image"})
                    base_url = "http://img.iamcook.ru/"
                    imgs_url = [urljoin(base_url, img["src"]) for img in imgs_url_soup]
                    calories_soup = soup.find_all("div", class_="energy tt")
                    calories = [amount.text for amount in calories_soup]
                    for element in range(len(titles)-1):
                        recipe = Dish(title=titles[element],
                                    description=descriptions[element],
                                    image=imgs_url[element],
                                    calories= calories[element],
                                    dishtype=dish_type,
                                    ingridients=ingredients[element],)
                        recipe.save()
