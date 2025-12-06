import csv
from tqdm import tqdm
import json

coords = {}

with open("2000-2025 geocode.csv") as f:
    r = csv.DictReader(f)

    for row in tqdm(r):
        cno = row["USER_CASE_NUMBER"]
        if cno.startswith("2024"):
            coords[cno] = (row["X"], row["Y"])

#print(coords)
json.dump(coords, open("case_geo_2024.json", "w"))