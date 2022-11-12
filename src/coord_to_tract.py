import csv
import time
from contextlib import closing

import pandas as pd
from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException


# Functions
def get_data(url):
    with closing(get(url, stream=True)) as resp:
        print(1.1)
        if good_response(resp):
            print(1.2)
            return resp.content
        else:
            print("Data retrieval failure")
            return None


def good_response(resp):
    content_type = resp.headers["Content-Type"].lower()
    return resp.status_code == 200 and content_type is not None and content_type.find("html") > -1


# Prep
f = open("tracts.csv", "w")
writer = csv.writer(f)

# Retrieving Data
df = pd.read_csv("long_lat.csv")

for index, row in df.iterrows():
    long = row["longitude"]
    lat = row["latitude"]

    link = (
        "https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x="
        + str(long)
        + "&y="
        + str(lat)
        + "&benchmark=2020&vintage=2020"
    )
    print(link)

    raw_data = get_data(link)
    print(1)
    org_data = BeautifulSoup(raw_data, "html.parser")

    # Finding Tract Numbers
    tract = "69"
    for span in org_data.find_all("span"):
        try:
            if span["class"] == ["resultItem"] and span.text == "TRACT CODE: ":
                tract = str(span.next_sibling)
        except:
            continue
    print(tract)
    writer.writerow([tract])
    time.sleep(10)
f.close()
