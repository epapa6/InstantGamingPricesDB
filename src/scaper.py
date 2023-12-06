from bs4 import BeautifulSoup
from game import Game
from datetime import date
import cloudscraper
import time
import json
import os

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

def load_or_create_json(file_path):
    """
    Loads JSON data from a file if it exists, otherwise returns an empty list.

    :param file_path: The path to the JSON file.
    :return: A list containing loaded JSON data or an empty list.
    """
    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            saved_games = json.load(json_file)
    else:
        saved_games = []
    return saved_games

def find_game_by_title(games, title):
    """
    Finds a game in the list based on its title.

    :param games: The list of games to search.
    :param title: The title of the game to find.
    :return: The game if found, otherwise None.
    """
    for game in games:
        if game["title"] == title:
            return game
    return None

def sort_by_price(game_dict):
    """
    Sorting key function to sort games by price.

    :param game_dict: The game dictionary.
    :return: The price or a default value for sorting.
    """
    if game_dict['price']:
        return game_dict['price']
    return float('inf')

# Initialize variables
start_time = time.time()
today = str(date.today().strftime("%d-%m-%Y"))
scraper = cloudscraper.create_scraper()
games = load_or_create_json('games.json')
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
        price = float(''.join(char for char in price_element.text.strip() if char.isdigit() or char == '.')) if price_element else None

        # Process game information
        current_game = None
        saved_game_with_title = find_game_by_title(games, title)

        if not saved_game_with_title:
            # Game is new
            current_game = Game(title, type, discount, price, price, False, "new", today)
        else:
            old_saved_game = Game.create_from_dict(saved_game_with_title)
            if (price and not old_saved_game.lowest) or (price and old_saved_game.lowest and price <= old_saved_game.lowest):
                if old_saved_game.lowest and price < old_saved_game.lowest:
                    # Game just got a lower price than the lowest
                    current_game = Game(title, type, discount, price, price, False, "updated", today)
                else:
                    # Game is par with the lowest price
                    current_game = Game(title, type, discount, price, price, False, "par", today)
            else:
                # Game is priced higher than the lowest 
                current_game = Game(title, type, discount, price, old_saved_game.lowest, False, "unchanged", old_saved_game.last_time_updated)
            games.remove(saved_game_with_title)

        games.append(current_game.to_dict())

# Process games with stock information
url_fragment_instock = "https://www.instant-gaming.com/it/ricerca/?platform%5B0%5D=1&type%5B0%5D=steam&sort_by=&min_reviewsavg=10&max_reviewsavg=100&noreviews=1&min_price=0&max_price=100&noprice=1&instock=1&gametype=all&search_tags=0&query=&page="

for index in range(1, get_last_page(url_fragment_instock + "1") + 1, 1):
    url_instock_page = url_fragment_instock + str(index)
    page = scraper.get(url_instock_page).text
    soup = BeautifulSoup(page, "html.parser")
    items = soup.find_all("div", class_="item force-badge")

    # Loop through items with stock information
    for item in items:
        game_title = item.find("span", class_="title").text.strip()
        saved_game_with_title = find_game_by_title(games, game_title) 
        current_game = Game.create_from_dict(saved_game_with_title)
        current_game.stock = True

        games.remove(saved_game_with_title)
        games.append(current_game.to_dict())

# Sort games by price
games.sort(key=sort_by_price)

# Save all games to a JSON file
with open('games.json', 'w') as json_file:
    json.dump(games, json_file, indent=2)

# Filter and save games with 'updated' or 'par' status to a separate file
par_or_updated_games = [game for game in games if (game.get("status") == "updated" or game.get("status") == "par")]

with open('games_par_or_updated.json', 'w') as json_file:
    json.dump(par_or_updated_games, json_file, indent=2)

# Print execution time
print("--- %s seconds ---" % (time.time() - start_time))