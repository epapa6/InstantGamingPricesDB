from bs4 import BeautifulSoup
from game import Game
from datetime import date
import cloudscraper
import time
import json

def get_last_page(url):
    """
    Retrieves the last page number from the pagination section of the given URL.

    :param url: The URL to fetch the last page number from.
    :return: The last page number.
    """
    page = scraper.get(url).text
    soup = BeautifulSoup(page, "html.parser")
    pagination = soup.find("ul", class_="pagination")
    return int(pagination.find_all("li")[3].text)

# Initialize variables
start_time = time.time()
today = str(date.today().strftime("%d-%m-%Y"))
scraper = cloudscraper.create_scraper()
games = []
url_fragment_search = "https://www.instant-gaming.com/it/ricerca/?platform%5B0%5D=pc&type%5B0%5D=steam&version=2&page="

# Loop through pages for games search
for index in range(1, get_last_page(url_fragment_search + "1") + 1, 1):
    url_search_page = url_fragment_search + str(index)
    page = scraper.get(url_search_page).text
    soup = BeautifulSoup(page, "html.parser")
    items = soup.find_all("div", class_="item force-badge")

    # Loop through items on the search page
    for item in items:
        # Extract game information
        title_element = item.find("span", class_="title")
        type_element = item.find("span", class_="dlc")
        discount_element = item.find("div", class_="discount")
        price_element = item.find("div", class_="price")

        title = title_element.text.strip() if title_element else None
        type = type_element.text.strip() if type_element else None
        discount = discount_element.text.strip() if discount_element else None
        price = price_element.text.strip() if price_element else None

        current_game = Game(title, type, discount, price, None, None, None, today)
        games.append(current_game.to_dict())

# Save all games to a JSON file
with open('games.json', 'w') as json_file:
    json.dump(games, json_file, indent=2)

# Print execution time
print("--- %s seconds ---" % (time.time() - start_time))