# Usage

First run `pip install -r requirements.txt`

```
[syntax] python csv_multi_decklist_difference.py _output_filename_ decklist_link1.com decklist_link2.com [...]
[example] python csv_multi_decklist_difference.py marneus_calgar.xlsx https://www.moxfield.com/decks/1izP28OO5kSEYGFf2UI-sw https://melee.gg/Decklist/View/322998 https://www.moxfield.com/decks/RwHQVfhso0yTNvuMMSXVig https://www.moxfield.com/decks/G8Ve84qOWEKntuRhhiI2tQ https://www.moxfield.com/decks/R06IiOFkMUGSpDKJqregUA https://www.moxfield.com/decks/NzDHcA166UWwegtDwDWTkA 
https://www.moxfield.com/decks/6ZQYUWWAo0muUMg8B1IZWg https://www.moxfield.com/decks/j3F6mQZkPUiqvbc7x1JlPA https://www.moxfield.com/decks/e2GD3_petky62jRTsjdhww https://www.moxfield.com/decks/RwHQVfhso0yTNvuMMSXVig
```

The output spreadsheet file will have card that are in all decks listed first, followed by cards that are not in all decks.

The "not in all decks section" has cards highlighted in red that are either 1. in only one deck, or 2. only NOT in one deck (i.e. in every other deck).

At the bottom, there is a sum of the number of outlying cards highlighted for each deck.
