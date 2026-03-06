import zipfile
import os
import shutil
from pypdf import PdfWriter, PdfReader

def process_files(zip_files, company, month):

    temp_folder = "temp"
    output_folder = "output"

    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
        
    os.makedirs(temp_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    for z in zip_files:
        with zipfile.ZipFile(z, 'r') as zip_ref:
            zip_ref.extractall(temp_folder)

    grouped_files = {}

    for file in os.listdir(temp_folder):
        if file.endswith(".pdf"):
            name_without_ext = file.replace(".pdf", "")
            
            if "_" in name_without_ext:
                suffix = name_without_ext.split("_")[-1].lower()
            else:
                suffix = name_without_ext[-3:].lower()

            if suffix not in grouped_files:
                grouped_files[suffix] = []
                
            grouped_files[suffix].append(os.path.join(temp_folder, file))

    merged_output_files = []

    for suffix, pdf_list in grouped_files.items():
        
        suffix_folder = os.path.join(output_folder, suffix)
        os.makedirs(suffix_folder, exist_ok=True)

        writer = PdfWriter()

        pdf_list.sort()

        for pdf in pdf_list:
            reader = PdfReader(pdf)
            for page in reader.pages:
                writer.add_page(page)

        final_pdf_name = f"{company}_{month}_{suffix}.pdf"
        output_file_path = os.path.join(suffix_folder, final_pdf_name)

        with open(output_file_path, "wb") as f:
            writer.write(f)

        merged_output_files.append(output_file_path)

    return merged_output_files