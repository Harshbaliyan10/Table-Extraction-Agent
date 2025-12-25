from paddleocr import PPStructure
from bs4 import BeautifulSoup
import os
import json
from PIL import Image
import numpy as np

engine = PPStructure(show_log=False)

def load_rgb_image(image_path):
    img = Image.open(image_path).convert("RGB")
    return np.array(img)

def table_html_to_json(html):
    soup = BeautifulSoup(html, "lxml")

    table = soup.find("table")
    if not table:
        return None

    rows = []
    for tr in table.find_all("tr"):
        row = []
        for td in tr.find_all(["td", "th"]):
            row.append(td.get_text(strip=True))
        rows.append(row)

    if not rows:
        return None

    headers = rows[0]
    data_rows = rows[1:]

    return {
        "headers": headers,
        "rows": data_rows
    }


def extract_tables(image_path):
    img = load_rgb_image(image_path)
    result = engine(img)

    tables = []
    for block in result:
        if block.get("type") == "table":
            html = block["res"].get("html", "")
            table_json = table_html_to_json(html)

            if table_json:
                tables.append({
                    "bbox": block.get("bbox"),
                    "table": table_json
                })

    return tables
def flatten_tables(image_name, tables):
    flat = []

    for table_index, table in enumerate(tables):
        table_data = table.get("table")
        if not table_data:
            continue

        headers = table_data.get("headers", [])
        rows = table_data.get("rows", [])

        for row_index, row in enumerate(rows):
            record = {
                "image": image_name,
                "table_id": table_index,
                "row_id": row_index
            }

            for i, header in enumerate(headers):
                key = header if header else f"col_{i}"
                value = row[i] if i < len(row) else None
                record[key] = value

            flat.append(record)

    return flat


def process_folder(folder):
    output = []

    for file in os.listdir(folder):
        if file.lower().endswith((".png", ".jpg", ".jpeg")):
            path = os.path.join(folder, file)

            tables = extract_tables(path)

            flat_rows = flatten_tables(file, tables)

            output.extend(flat_rows)


    return output


if __name__ == "__main__":
    data = process_folder("images")
    print(json.dumps(data, indent=2, ensure_ascii=False))
