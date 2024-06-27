import time
import requests
from bs4 import BeautifulSoup  # For parsing HTML content
import csv
from url_extensions import prefectures, games  # Importing the prefectures and games data

def get_total_results(url):
    headers = {  # Include cookies if necessary (refer to previous explanation)
        "Cookie": "facility_dspcount=50",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    result_count_element = soup.find('div', class_='cl_search_result')

    if result_count_element:
        # Extract only the numeric part (replace with a more robust pattern if needed)
        num_str = result_count_element.text.replace('件', ' ').split()[0]

        try:
            total_results = int(num_str)
            return total_results
        except ValueError:
            print(f"Error converting number: {num_str}")
            return None  # Indicate failure

    else:
        print("Could not find total results count.")
        return None  # Indicate failure to find total results count
    
def get_store_data(store_data, prefecture_name, prefecture, game):
    headers = {
            # Include cookies from browser's "Request Headers" (if necessary)
            "Cookie": "facility_dspcount=50",  # Replace with actual cookie values
        }
    base_url = f"https://p.eagate.573.jp/game/facility/search/p/list.html?{game['value']}&paselif=false{prefecture.get('url_extension', '')}&finder=area"
    total_results = get_total_results(base_url)
    if not total_results:
        return store_data

    # Calculate number of pages (assuming 50 results per page)
    num_pages = (total_results // 50) + (total_results % 50 > 0)  # Add 1 if there's a remainder

    for page_number in range(1, num_pages + 1):
        page_url = f"{base_url}&page={page_number}"
        response = requests.get(page_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        store_elements = soup.find_all('div', class_='cl_shop_bloc')

        for store_element in store_elements:
            # Check if location already exists in store_data
            location_name = store_element.get('data-name')
            if location_name in store_data:
                # Update game availability for existing location
                store_data[location_name][game['key']] = True # Set current game key as supported for the existing location
            else:
                # Create new store info for a new location
                store_info = {
                    "name": location_name,
                    "address": store_element.get('data-address'),
                    "latitude": store_element.get('data-latitude'),
                    "longitude": store_element.get('data-longitude'),
                    "paseli_enabled": False,  # Assume Paseli is disabled by default
                    "region": prefecture['region'],
                    "prefecture": prefecture_name,
                    "SDVX_VM": False,
                    "IIDX_LM": False,
                    "IIDX": False,
                    "DDR_Gold": False,
                    "DDR": False,
                    "Pol_Chord": False,
                    "Gitadora_GF": False,
                    "Gitadora_DM": False,
                    "jubeat": False,
                    "Popn": False,
                    "DaR": False,
                    "Nostalgia": False,
                    "DRS": False,
                    "Reflec": False,
                    "Museca": False,
                    "Dance_Evo": False,
                    "Paseli_Charge": False,
                }
                # Set current game as supported for the new location
                store_info[game['key']] = True

                # Check for Paseli element in html response
                paseli_element = store_element.find('div', class_='cl_shop_paseli')
                if paseli_element:
                    store_info["paseli_enabled"] = True

                # Add new store info to store_data dictionary
                store_data[location_name] = store_info

    return store_data



def save_to_csv(data, filename, encoding='utf-8-sig'):
    with open(filename, 'w', newline='', encoding=encoding) as csvfile:
        # Get fieldnames from the first data point in the dictionary
        fieldnames = next(iter(data.values())).keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for store in data.values():
            writer.writerow(store)


def main():
    all_store_data = {}
    #for loops to iterate through prefectures and games found in url-extensions.py
    for prefecture_name, prefecture in prefectures.items():
        for game_name, game_value in games.items():
            game = {'key': game_name, 'value': game_value}
            print(f"Getting store data for {game_name} in {prefecture_name}")
            all_store_data = get_store_data(all_store_data, prefecture_name, prefecture, game)
            time.sleep(0.1)

    save_to_csv(all_store_data, "store_data.csv")
    print("Store data saved to store_data.csv")

if __name__ == "__main__":
    main()
