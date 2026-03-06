import zipfile
import os
from pypdf import PdfWriter, PdfReader


def process_files(zip_files):

    temp_folder = "temp"
    output_folder = "output"

    os.makedirs(temp_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    pdf_files = []

    # unzip zip
    for z in zip_files:

        with zipfile.ZipFile(z, 'r') as zip_ref:
            zip_ref.extractall(temp_folder)

    # หา pdf
    for file in os.listdir(temp_folder):

        if file.endswith(".pdf"):
            pdf_files.append(os.path.join(temp_folder, file))

    # merge pdf
    writer = PdfWriter()

    for pdf in pdf_files:

        reader = PdfReader(pdf)

        for page in reader.pages:
            writer.add_page(page)

    output_file = os.path.join(output_folder, "merged.pdf")

    with open(output_file, "wb") as f:
        writer.write(f)

    return output_file