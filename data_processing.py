import pandas as pd

# xlsx data reader
def genselx(xlsx_name):
    df = pd.read_excel(xlsx_name)

    matches = []
    for _, row in df.iterrows():
        match_data = {
            "match": row["TEAMS"],
            "categories": []
        }

        for col in df.columns[2:]:
            category = {
                "name": col,
                "value": int(row[col]) if not pd.isna(row[col]) else 0  # Default to 0 for NaN
            }
            match_data["categories"].append(category)

        matches.append(match_data)

    return matches
