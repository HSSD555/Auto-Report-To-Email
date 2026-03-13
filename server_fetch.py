import requests
from bs4 import BeautifulSoup
import os
import shutil

BASE_URL = "http://202.94.242.115/auto_report/"


def get_available_months():

    r = requests.get(BASE_URL)

    soup = BeautifulSoup(r.text, "html.parser")

    months = []

    for link in soup.find_all("a"):

        name = link.get("href")

        if name and "_" in name and name.endswith("/"):

            months.append(name.replace("/", ""))

    months.sort(reverse=True)

    return months


def get_companies_from_month(month):

    folder_url = f"{BASE_URL}/{month}/"

    r = requests.get(folder_url)

    soup = BeautifulSoup(r.text, "html.parser")

    companies = set()

    for link in soup.find_all("a"):

        name = link.get("href")

        if name and name.endswith(".zip"):

            company = name.replace(".zip", "")

            companies.add(company)

    return sorted(list(companies))


def fetch_company_files(company, month):

    folder_url = f"{BASE_URL}/{month}/"

    r = requests.get(folder_url)

    soup = BeautifulSoup(r.text, "html.parser")

    download_folder = "downloads"

    if os.path.exists(download_folder):
        shutil.rmtree(download_folder)

    os.makedirs(download_folder, exist_ok=True)

    downloaded = []

    for link in soup.find_all("a"):

        file_name = link.get("href")

        if not file_name:
            continue

        if file_name.startswith(company) and file_name.endswith(".zip"):

            file_url = folder_url + file_name

            response = requests.get(file_url)

            save_path = f"{download_folder}/{file_name}"

            with open(save_path, "wb") as f:
                f.write(response.content)

            downloaded.append(save_path)

    return downloaded