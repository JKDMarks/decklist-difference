import sys
import argparse
import requests

from selenium import webdriver
from time import sleep

from selenium.webdriver.common.by import By


def get_full_commander_name(name):
    if name == None:
        return None

    data = requests.get(f"https://api.scryfall.com/cards/search?q={name}").json()[
        "data"
    ]
    if len(data) > 1:
        print("*** More than one commander found")
        print("\n".join(card["name"] for card in data))
        exit(1)
    else:
        return data[0]["name"]


def run(url, max_pos):
    driver = webdriver.Chrome()
    driver.get(url)
    sleep(2)
    links = [
        a_tag.get_attribute("href")
        for a_tag in driver.find_elements(By.CSS_SELECTOR, "table a")
    ]
    standings = [
        int(node.text)
        for node in driver.find_elements(By.CSS_SELECTOR, "tbody tr td:nth-child(3)")
    ]
    driver.quit()
    endpoint = next(idx for idx, val in enumerate(standings) if val > max_pos)
    links = links[:endpoint]
    print(" ".join(links))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch decklist links from edhtop16.com"
    )
    parser.add_argument("-c1", "--commander1", required=True)
    parser.add_argument("-c2", "--commander2")
    parser.add_argument("-m", "--maximum", required=True, type=int)
    args = parser.parse_args()
    commander1 = get_full_commander_name(args.commander1)
    commander2 = get_full_commander_name(args.commander2)

    base_url = "https://edhtop16.com/commander/"
    base_url += commander1
    if commander2:
        base_url += " + " + commander2
    run(base_url, args.maximum)
