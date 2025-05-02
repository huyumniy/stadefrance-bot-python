from random import choice
import re

def find_category_value(categories, category_name):
    category_dict = {category['name']: category['value'] for category in categories}
    return category_dict.get(category_name)


def ua():
    with open('uas') as ugs:
        uas=[x.strip() for x in ugs.readlines()]
        ugs.close()
    return choice(uas)


def parse_seat_info(seat_info):
    # Returns section, block, row(int), seat(int)
    section, block, row_str, seat_str = seat_info.split(' - ')
    return section, block, row_str, int(seat_str)


def match_seat_info(text: str) -> str | None:
    """
    If `text` contains a valid block-row-seat triplet (e.g. "Y14 - 59 - 34"),
    returns the entire string back; otherwise returns None.
    """
    _seat_re = re.compile(
        r"""
        ^                                   # start of string
        (?P<prefix>.+?)\s*-\s*              # anything (e.g. "Tribune inter SUD"), then " - "
        (?P<block>[A-Z]\d+)\s*-\s*          # block: letter+digits
        (?P<row>\d+)\s*-\s*                 # row: digits
        (?P<seat>\d+)                       # seat: digits
        $                                   # end of string
        """,
        re.VERBOSE
    )
    match = _seat_re.match(text)
    return match.group(0) if match else None
