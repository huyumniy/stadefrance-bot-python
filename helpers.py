from random import choice

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
