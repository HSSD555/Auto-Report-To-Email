import zipfile
import os
import shutil
import math
import subprocess 
import glob
from pypdf import PdfWriter, PdfReader

def process_files(zip_files, company, month):
    temp_folder = "temp"
    output_folder = "output"
    seven_zip_path = r"C:\Program Files\7-Zip\7z.exe" 
    has_7z = os.path.exists(seven_zip_path)
    
    if os.path.exists(temp_folder): 
        shutil.rmtree(temp_folder)
    os.makedirs(temp_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    old_parts = glob.glob(os.path.join(output_folder, f"*{company}*PART*"))
    for f in old_parts:
        try: os.remove(f)
        except: pass

    all_extracted_files = []
    
    for z in zip_files:
        if not os.path.exists(z): continue
        try:
            with zipfile.ZipFile(z, "r") as zip_ref:
                for member in zip_ref.namelist():
                    if member.lower().endswith(".pdf") and not member.startswith("__MACOSX"):
                        filename = os.path.basename(member)
                        if filename:
                            target_path = os.path.join(temp_folder, filename)
                            with zip_ref.open(member) as source, open(target_path, "wb") as target:
                                shutil.copyfileobj(source, target)
                            if target_path not in all_extracted_files:
                                all_extracted_files.append(target_path)
        except Exception as e: 
            print(f"❌ Error: {e}")

    all_extracted_files.sort()
    total_files = len(all_extracted_files)

    final_writer = PdfWriter()
    valid_pdf_count = 0
    for pdf in all_extracted_files:
        try:
            reader = PdfReader(pdf)
            for page in reader.pages:
                final_writer.add_page(page)
            valid_pdf_count += 1
        except: pass
    
    final_report = os.path.join(output_folder, f"{company}_{month}_REPORT.pdf")
    if valid_pdf_count > 0:
        with open(final_report, "wb") as f:
            final_writer.write(f)
    else:
        final_report = ""

    zipped_parts = []
    if "TMB_TRUE" in company.upper() and total_files > 0:
        chunk_size = math.ceil(total_files / 3) 
        for i in range(3):
            start_idx = i * chunk_size
            end_idx = start_idx + chunk_size
            current_chunk = all_extracted_files[start_idx:end_idx]
            
            if not current_chunk: continue
            
            ext = ".7z" if has_7z else ".zip"
            zip_name = f"{company}_{month}_PART{i+1}{ext}"
            zip_path = os.path.join(output_folder, zip_name)
            
            list_file = os.path.join(temp_folder, f"list_part_{i+1}.txt")
            with open(list_file, "w", encoding="utf-8") as f:
                for item in current_chunk:
                    f.write(f"{item}\n")

            if has_7z:
                try:
                    subprocess.run([
                        seven_zip_path, "a", zip_path, 
                        f"@{list_file}", 
                        "-mx=9",       
                        "-m0=lzma2",   
                        "-ms=on",      
                        "-y"
                    ], check=True, stdout=subprocess.DEVNULL)
                    zipped_parts.append(zip_path)
                except:
                    has_7z = False 
            
            if not has_7z:
                zip_path_fb = zip_path.replace(".7z", ".zip")
                with zipfile.ZipFile(zip_path_fb, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for f_path in current_chunk:
                        zf.write(f_path, os.path.basename(f_path))
                zipped_parts.append(zip_path_fb)

    return all_extracted_files, final_report, sorted(list(set(zipped_parts)))