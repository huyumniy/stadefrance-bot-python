from random import choice

def find_category_value(categories, category_name):
    category_dict = {category['name']: category['value'] for category in categories}
    return category_dict.get(category_name)


def ua():
    with open('uas') as ugs:
        uas=[x.strip() for x in ugs.readlines()]
        ugs.close()
    return choice(uas)
