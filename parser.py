import requests
from bs4 import BeautifulSoup
import argparse



def get_coock_recipe(url):
	response = requests.get(url)
	response.raise_for_status()
	soup = BeautifulSoup(response.text, 'html.parser')
	header = soup.find_all("div", {"class": "header"})
	return header


def parse_recipe(recipe_id):
	url = f"https://www.iamcook.ru{recipe_id}"
	response = requests.get(url)
	response.raise_for_status()
	soup = BeautifulSoup(response.text, 'html.parser')
	return soup


def main():
	parser = argparse.ArgumentParser(description="")
	parser.add_argument('start_id', type=int,
                        help='ID of the recipe to start parsing from')
	parser.add_argument('end_id', type=int,
                        help='ID of the last recipe to parse')
	args = parser.parse_args()
	start_args = args.start_id
	end_args = args.end_id


if __name__ == "__main__":
    main()
