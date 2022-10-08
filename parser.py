import requests
import collections
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
collections.Callable = collections.abc.Callable


def parse_recipe(url, pages, dish_type):
	recipes_list = []
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
			recipes ={
						"dishtype": dish_type,	
						"title": "",
						"description": "",
						"ingredients": "",
						"imgs_url": "",
						"calories": "",
			}
			recipes["dishtype"] = dish_type
			recipes["title"] = titles[element]
			recipes["description"] = descriptions[element]
			recipes["ingredients"] = ingredients[element]
			recipes["imgs_url"] = imgs_url[element]
			recipes["calories"] = calories[element]
			recipes_list.append(recipes)
	return recipes_list


def main():
	pages = 4
	vegetaian_url = "https://www.iamcook.ru/event/everyday/everyday-vegetarian"
	nonglyuten_url = 'https://www.iamcook.ru/event/baking/gluten-free-baking'
	meat_url = "https://www.iamcook.ru/showsubsection/myasnie_bluda"
	veg_list = parse_recipe(vegetaian_url, pages, dish_type="Вегетарианская")
	nonglyuten_list = parse_recipe(nonglyuten_url, pages, dish_type="Безглютеновая")
	meat_list = parse_recipe(meat_url, pages, dish_type="Мясные блюда")
	recipes_list = veg_list + nonglyuten_list + meat_list
	with open('recipes.json', 'a') as fp:
		json.dump(
            recipes_list,
            fp,
			ensure_ascii=False,
            indent=4
        )


if __name__ == "__main__":
    main()
