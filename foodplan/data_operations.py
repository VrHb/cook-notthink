import json

def get_dishes_from_json() -> list[dict]:
    with open("recipes.json", "r", encoding="utf-8") as file:
        dishes = json.load(file)
    return dishes
