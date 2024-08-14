import os
import sys
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
from fetch_decklist_from_link import fetch_decklist_from_url

OUTPUT_DIRNAME = 'outputs'

def write_to_xlsx(
    deck_dicts,
    deck_names,
    deck_links,
    cards_in_all_decks,
    cards_in_two_or_more_decks,
    output_filename,
):
    workbook = xlsxwriter.Workbook(output_filename)
    worksheet = workbook.add_worksheet()
    format_red_border_bold = workbook.add_format(
        {"bg_color": "#ffcccc", "font_color": "#cc0000", "bold": True, "border": 1}
    )

    # TODO: Add deck creator name on 2nd line
    deck_names_with_links = [
        "\n".join(name_link) for name_link in zip(deck_names, deck_links)
    ]
    headers = ["Card Name", "Number of Decks", *deck_names_with_links]
    row = 1
    worksheet.write_row(0, 0, headers)
    worksheet.set_row(0, 30)

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
    worksheet.set_column(1, len(headers), 30)
    worksheet.freeze_panes(1, 1)
    b1 = xl_rowcol_to_cell(start_row, 1)
    c1 = xl_rowcol_to_cell(start_row, 2)
    z99 = xl_rowcol_to_cell(end_row, len(headers) - 1)
    c_cell_range = f"{c1}:{z99}"

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

    workbook.close()


def run(
    deck_names: list[str],
    deck_dicts: list[dict[str, int]],
    deck_links: list[str],
    output_filename,
):
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
        deck_links=deck_links,
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

    if not os.path.exists(OUTPUT_DIRNAME):
        os.mkdir(OUTPUT_DIRNAME)

    run(
        deck_names=deck_names,
        deck_dicts=deck_dicts,
        deck_links=deck_links,
        output_filename=f'{OUTPUT_DIRNAME}/{output_filename}',
    )
