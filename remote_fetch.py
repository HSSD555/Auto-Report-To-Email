import requests
from bs4 import BeautifulSoup
import os

BASE_URL = "http://202.94.242.115/auto_report/2026_02/"

def get_zip_links():

    res = requests.get(BASE_URL)

    soup = BeautifulSoup(res.text, "html.parser")

    links = []

    for a in soup.find_all("a"):

        href = a.get("href")

        if href.endswith(".zip"):
            links.append(BASE_URL + href)

    return links


def download_files():

    os.makedirs("downloads", exist_ok=True)

    files = get_zip_links()

    downloaded = []

    for url in files:

        filename = url.split("/")[-1]

        path = f"downloads/{filename}"

        r = requests.get(url)

        with open(path, "wb") as f:
            f.write(r.content)

        downloaded.append(path)

    return downloaded