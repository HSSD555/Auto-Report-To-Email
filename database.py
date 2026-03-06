import os

BASE_FOLDER = "reports"

def get_zip_files(company, month):

    folder = os.path.join(BASE_FOLDER, company, month)

    if not os.path.exists(folder):
        return []

    files = []

    for f in os.listdir(folder):

        if f.endswith(".zip"):
            files.append(os.path.join(folder, f))

    return files