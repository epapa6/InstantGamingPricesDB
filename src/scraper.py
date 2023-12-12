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
            games = json.load(json_file)
    else:
        games = []
    return games

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
games_new, games_updated, games_par, games_unchanged = (0, 0, 0, 0)
url_fragment_search = "https://www.instant-gaming.com/it/ricerca/?currency=EUR&?platform%5B0%5D=1&type%5B0%5D=steam&sort_by=&min_reviewsavg=10&max_reviewsavg=100&noreviews=1&min_price=0&max_price=100&noprice=1&instock=0&gametype=all&search_tags=0&query=&page="

# Loop through pages for games search
for index in range(1, get_last_page(url_fragment_search + "1") + 1, 1):
    url_page = url_fragment_search + str(index)
    page = scraper.get(url_page).text
    soup = BeautifulSoup(page, "html.parser")

    location = soup.find("span", class_="localisation")
    print(location.text)

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
        saved_game = find_game_by_title(games, title)

        if not saved_game:
            # Game is new
            current_game = Game(title, type, discount, price, price, False, "new", today)
            games_new += 1
        else:
            old_game = Game.create_from_dict(saved_game)
            if (price and not old_game.lowest) or (price and old_game.lowest and price <= old_game.lowest):
                if old_game.lowest and price < old_game.lowest:
                    # Game just got a lower price than the lowest
                    current_game = Game(title, type, discount, price, price, False, "updated", today)
                    games_updated += 1
                else:
                    # Game is par with the lowest price
                    current_game = Game(title, type, discount, price, price, False, "par", today)
                    games_par += 1
            else:
                # Game is priced higher than the lowest 
                current_game = Game(title, type, discount, price, old_game.lowest, False, "unchanged", old_game.last_time_updated)
                games_unchanged += 1
            games.remove(saved_game)

        games.append(current_game.to_dict())

# Process games with stock information
url_fragment_search_instock = "https://www.instant-gaming.com/it/ricerca/?currency=EUR&?platform%5B0%5D=1&type%5B0%5D=steam&sort_by=&min_reviewsavg=10&max_reviewsavg=100&noreviews=1&min_price=0&max_price=100&noprice=1&instock=1&gametype=all&search_tags=0&query=&page="

for index in range(1, get_last_page(url_fragment_search_instock + "1") + 1, 1):
    url_instock_page = url_fragment_search_instock + str(index)
    page = scraper.get(url_instock_page).text
    soup = BeautifulSoup(page, "html.parser")
    items = soup.find_all("div", class_="item force-badge")

    # Loop through items with stock information
    for item in items:
        game_title = item.find("span", class_="title").text.strip()
        saved_game = find_game_by_title(games, game_title) 
        current_game = Game.create_from_dict(saved_game)
        current_game.stock = True

        games.remove(saved_game)
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

# Print stats about status of the game
print("Number of games: ", games_new + games_updated + games_par + games_unchanged)
print("New games: ", games_new)
print("Updated games: ", games_updated)
print("Par games: ", games_par)
print("Unchanged games: ", games_unchanged)

# Print execution time
print("--- %s seconds ---" % (time.time() - start_time))