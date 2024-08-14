from urllib.parse import urlparse
from bs4 import BeautifulSoup
import json
import requests
import sys
import re


def _parse_deck_dict_from_deck_list(deck_list: list[str]):
    deck_dict = {}
    for qty, cardname in (
        card.split(" ", 1)
        for card in deck_list
        if len(card) > 0 and card[0].isnumeric()
    ):
        deck_dict[cardname] = deck_dict.get(cardname, 0) + int(qty)

    return deck_dict


def _fetch_decklist_from_archidekt(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    data = json.loads(soup.select_one("script#__NEXT_DATA__").text)
    deck_name = data["props"]["pageProps"]["redux"]["deck"]["name"]
    cards = list(data["props"]["pageProps"]["redux"]["deck"]["cardMap"].values())

    deck_dict = {}
    for card in cards:
        if (
            "Maybeboard" not in card["categories"]
            and "Sideboard" not in card["categories"]
        ):
            deck_dict[card["name"]] = card["qty"]

    return deck_dict, deck_name


def _fetch_decklist_from_moxfield(url):
    moxfield_api_base = "https://api2.moxfield.com/v3/decks/all/"
    data = requests.get(moxfield_api_base + url.split("/decks/")[1]).json()
    if "name" not in data:
        print(data)
        raise Exception("Error for url " + url)
    deck_name = data["name"]
    cards = list(data["boards"]["mainboard"]["cards"].values()) + list(
        data["boards"]["commanders"]["cards"].values()
    )

    deck_dict = {}
    for card in cards:
        deck_dict[card["card"]["name"]] = card["quantity"]

    return deck_dict, deck_name


def _fetch_decklist_from_melee(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    deck_name = re.sub(
        r"\n+", r" ", soup.select_one(".decklist-card-info-row").text
    ).strip()
    deck_str = soup.select_one(".decklist-builder-copy-button")["data-clipboard-text"]
    deck_list = re.split(r"\r?\n", deck_str)
    deck_dict = _parse_deck_dict_from_deck_list(deck_list)

    return deck_dict, deck_name


def fetch_decklist_from_url(url):
    if "archidekt.com" in url.lower():
        return _fetch_decklist_from_archidekt(url)
    if "moxfield.com" in url.lower():
        return _fetch_decklist_from_moxfield(url)
    if "melee.gg" in url.lower():
        return _fetch_decklist_from_melee(url)


if __name__ == "__main__":
    url = sys.argv[1]
    deck_dict, deck_name = fetch_decklist_from_url(url)
    breakpoint()
    print(deck_dict, deck_name)
