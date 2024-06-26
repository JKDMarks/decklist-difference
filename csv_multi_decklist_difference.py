# from io import TextIOWrapper
# import csv
import sys
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
from fetch_decklist_from_link import fetch_decklist_from_url


# def decklist_file_to_dict(deck: TextIOWrapper):
#     deck_arr = deck.read().split("\n")
#     return {
#         cardname: int(qty)
#         for qty, cardname in (
#             card.split(" ", 1)
#             for card in deck_arr
#             if len(card) > 0 and card[0].isnumeric()
#         )
#     }


def write_to_xlsx(
    deck_dicts,
    deck_names,
    cards_in_all_decks,
    cards_in_two_or_more_decks,
    output_filename,
):
    workbook = xlsxwriter.Workbook(output_filename)
    worksheet = workbook.add_worksheet()
    format_green = workbook.add_format({"bg_color": "#ccffcc", "font_color": "#006600"})
    format_green_border_bold = workbook.add_format(
        {"bg_color": "#ccffcc", "font_color": "#006600", "bold": True, "border": 1}
    )
    format_red = workbook.add_format({"bg_color": "#ffcccc", "font_color": "#cc0000"})
    format_red_border_bold = workbook.add_format(
        {"bg_color": "#ffcccc", "font_color": "#cc0000", "bold": True, "border": 1}
    )

    headers = ["Card Name", "Number of Decks", *deck_names]
    row = 1
    worksheet.write_row(0, 0, headers)

    for card in sorted(cards_in_all_decks):
        worksheet.write_row(
            row, 0, [card, len(deck_names), *[dd.get(card, 0) for dd in deck_dicts]]
        )
        row += 1

    num_outliers = [0] * len(deck_dicts)
    start_row = row
    for card in sorted(cards_in_two_or_more_decks):
        card_qtys_in_decks = [dd.get(card, 0) for dd in deck_dicts]
        num_decks_containing = [num > 0 for num in card_qtys_in_decks].count(True)
        for i in range(len(card_qtys_in_decks)):
            if (num_decks_containing == 1 and card_qtys_in_decks[i] > 0) or (
                num_decks_containing == len(deck_dicts) - 1
                and card_qtys_in_decks[i] == 0
            ):
                num_outliers[i] += 1

        worksheet.write_row(
            row,
            0,
            [card, num_decks_containing, *card_qtys_in_decks],
        )
        row += 1
    end_row = row

    worksheet.write_row(end_row + 1, 0, ["Total Difference", "", *num_outliers])

    worksheet.autofit()
    worksheet.freeze_panes(1, 0)
    a1 = xl_rowcol_to_cell(start_row, 0)
    a99 = xl_rowcol_to_cell(end_row, 0)
    b1 = xl_rowcol_to_cell(start_row, 1)
    c1 = xl_rowcol_to_cell(start_row, 2)
    z99 = xl_rowcol_to_cell(end_row, len(headers) - 1)
    cell_range = f"{a1}:{z99}"
    c_cell_range = f"{c1}:{z99}"
    cell_range_excluding_b = f"${a1}:${a99},${b1}:${z99}"
    # format_range = (start_row, 0, end_row, len(headers))

    worksheet.conditional_format(
        c_cell_range,
        {
            "type": "formula",
            "format": format_red_border_bold,
            "criteria": f"=AND(${b1}={len(deck_names) - 1}, {c1}=0, ISNUMBER({c1}))",
        },
    )
    worksheet.conditional_format(
        c_cell_range,
        {
            "type": "formula",
            "format": format_red_border_bold,
            "criteria": f"=AND(${b1}=1, {c1}>0, ISNUMBER({c1}))",
        },
    )
    # worksheet.conditional_format(
    #     cell_range,
    #     {
    #         "type": "formula",
    #         "format": format_green,
    #         "criteria": f"=(${b1}={len(deck_names) - 1})",
    #     },
    # )
    # worksheet.conditional_format(
    #     cell_range,
    #     {
    #         "type": "formula",
    #         "format": format_red,
    #         "criteria": f"=(${b1}=1)",
    #     },
    # )

    workbook.close()


def run(deck_names: list[str], deck_dicts: list[dict[str, int]], output_filename):
    deck_sets: list[set[str]] = [set(dd.keys()) for dd in deck_dicts]
    cards_in_all_decks = deck_sets[0].copy()
    _cards_in_any_deck = deck_sets[0].copy()
    for deck in deck_sets[1:]:
        cards_in_all_decks.intersection_update(deck)
        _cards_in_any_deck.update(deck)
    cards_in_two_or_more_decks = _cards_in_any_deck - cards_in_all_decks

    write_to_xlsx(
        deck_dicts=deck_dicts,
        deck_names=deck_names,
        cards_in_all_decks=cards_in_all_decks,
        cards_in_two_or_more_decks=cards_in_two_or_more_decks,
        output_filename=output_filename,
    )


if __name__ == "__main__":
    [_, output_filename, *deck_links] = sys.argv
    deck_dicts = []
    deck_names = []

    for url in deck_links:
        dd, dn = fetch_decklist_from_url(url)
        deck_dicts.append(dd)
        deck_names.append(dn)
    # for dn in deck_names:
    #     with open(dn, "r") as f:
    #         deck_dicts.append(decklist_file_to_dict(f))
    run(deck_names, deck_dicts, output_filename)
