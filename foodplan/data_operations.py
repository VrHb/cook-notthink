import json
from typing import NamedTuple


class Dish(NamedTuple):
    category: str
    title: str
    description: str
    ingridients: str
    image: str
    calories: str


def get_dishes_from_json() -> list[dict]:
    with open("recipes.json", "r", encoding="utf-8") as file:
        dishes = json.load(file)
    return dishes
