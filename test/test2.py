## https://towardsdatascience.com/read-data-from-google-sheets-into-pandas-without-the-google-sheets-api-5c468536550
import pandas as pd

sheet_id = "144wxY9kdNAm68hySqE9-1pUvuKSzZiaYHdqT0-wEdWk"
sheet_name = "Sheet1"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

r = pd.read_csv(url)
print(r)