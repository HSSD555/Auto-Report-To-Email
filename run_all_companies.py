from server_fetch import get_companies_from_month, fetch_company_files
from automation import process_files
from logger import log
import os
import json
import glob
import shutil

def run_all(month):
    """
    ฟังก์ชันเตรียมไฟล์เฉพาะบริษัทใน Config และล้างไฟล์เก่าก่อนเริ่ม
    """
    try:
        with open("companies.json", encoding="utf-8") as f:
            email_map = json.load(f)
    except Exception as e:
        log(f"Error loading companies.json: {e}")
        return []

    if os.path.exists("output"):
        for old_file in glob.glob("output/*.pdf") + glob.glob("output/*.7z"):
            try: os.remove(old_file)
            except: pass
        print("🧹 ล้างไฟล์เก่าใน output เรียบร้อย")

    all_companies = get_companies_from_month(month)
    results = []

    if not all_companies:
        log(f"Warning: No companies found for {month}")
        return []

    target_companies = []
    for comp in all_companies:
        comp_up = comp.upper().strip()
        if any(key.upper().strip() in comp_up for key in email_map):
            target_companies.append(comp)

    print(f"🔄 เริ่มเตรียมไฟล์สำหรับ {len(target_companies)} บริษัท...")

    for company in target_companies:
        try:
            print(f"🚀 กำลังเตรียมไฟล์: {company}")
            files = fetch_company_files(company, month)
            if not files: continue

            sub_pdfs, final_report, zip_parts = process_files(files, company, month)

            if os.path.exists(final_report):
                results.append({
                    "company": company,
                    "report_path": final_report,
                    "zip_parts": zip_parts
                })
                log(f"✅ Prepared: {company}")
        except Exception as e:
            log(f"❌ Error preparing {company}: {str(e)}")
            
    return results