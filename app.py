import streamlit as st
import pandas as pd
import os
import json
import zipfile
import time
import datetime
import glob 
import re

from automation import process_files
from send_mail import send_email
from server_fetch import (
    get_available_months,
    get_companies_from_month,
    fetch_company_files
)
from logger import log
from run_all_companies import run_all 

st.set_page_config(page_title="Company Report Portal", page_icon="📊", layout="wide")

def get_comp_config(company_name, email_map):
    """หา Config จาก JSON โดยใช้ Keyword Matching"""
    name_up = company_name.upper().strip()
    for key in email_map:
        if key.upper().strip() in name_up:
            return email_map[key], key
    return {}, None

def get_month_en(month_text):
    """แปลงเดือนไทยเป็นอังกฤษ"""
    months_map = {
        "มกราคม": "January", "กุมภาพันธ์": "February", "มีนาคม": "March",
        "เมษายน": "April", "พฤษภาคม": "May", "มิถุนายน": "June",
        "กรกฎาคม": "July", "สิงหาคม": "August", "กันยายน": "September",
        "ตุลาคม": "October", "พฤศจิกายน": "November", "ธันวาคม": "December"
    }
    for th, en in months_map.items():
        if th in month_text:
            year_match = re.search(r'\d{4}', month_text)
            year_en = year_match.group() if year_match else str(datetime.datetime.now().year)
            if int(year_en) > 2500: year_en = str(int(year_en)-543)
            return f"{en} {year_en}"
    return month_text

@st.dialog("📧 รายละเอียดการส่งรายงาน")
def send_email_dialog(company_name, report_paths, month, email_map):
    if isinstance(report_paths, str):
        report_paths = [report_paths]
    
    actual_files = [p for p in report_paths if os.path.exists(p)]
    if not actual_files:
        st.error("❌ ไม่พบไฟล์ที่จะส่ง!")
        return

    comp_info, json_key = get_comp_config(company_name, email_map)
    db_email = comp_info.get("email", "")
    month_en = get_month_en(month)
    issue_no = f"{datetime.datetime.now().strftime('%Y%m%d')}1028"
    
    display_name = json_key if json_key else company_name
    
    raw_subject = comp_info.get("subject", "สรุปรายงานประจำเดือน {month} - {company}")
    raw_body = comp_info.get("body", "เรียน ทีมงาน {company},\n\nระบบได้ดำเนินการจัดทำรายงานเรียบร้อยแล้ว")
    
    footer = "\n\nShould you experience any issues, please contact Service Desk at 02-016-5678" if any(x in company_name.upper() for x in ["AYCAP", "AYUINS"]) else ""

    st.markdown(f"### บริษัท: **{display_name}**")
    email_type = st.radio("เลือกผู้รับ:", ["ลูกค้า (Direct)", "ทีมภายใน", "ระบุเอง"], horizontal=True, key=f"radio_{company_name}")
    target_email = db_email if email_type == "ลูกค้า (Direct)" else ("ITService0403@gmail.com" if email_type == "ทีมภายใน" else "")
    final_email = st.text_input("ส่งไปที่อีเมล:", value=target_email, key=f"input_{company_name}")
    
    st.divider()
    
    try:
        formatted_subject = raw_subject.format(month=month, company=display_name, month_en=month_en)
        formatted_body = raw_body.format(month=month, company=display_name, month_en=month_en, issue_no=issue_no) + footer
    except KeyError as e:
        st.warning(f"⚠️ JSON ขาดตัวแปร {e} ระบบจะใช้ค่าพื้นฐานแทน")
        formatted_subject = raw_subject
        formatted_body = raw_body

    final_subject = st.text_input("หัวข้อเมล:", value=formatted_subject, key=f"subj_{company_name}")
    final_body = st.text_area("เนื้อหาเมล:", value=formatted_body, height=250, key=f"body_{company_name}")

    if st.button("🚀 ยืนยันและเริ่มส่งเมล", type="primary", use_container_width=True):
        try:
            is_tmb = "TMB_TRUE" in company_name.upper()
            if is_tmb and len(actual_files) > 1:
                for idx, f_path in enumerate(actual_files):
                    p_subj = f"{final_subject} (Part {idx+1}/{len(actual_files)})"
                    send_email(final_email, [f_path], subject=p_subj, body=final_body)
                    time.sleep(1.5)
            else:
                send_email(final_email, actual_files, subject=final_subject, body=final_body)
            st.success("✅ ส่งเรียบร้อยแล้ว!")
            log(f"Sent success: {company_name}")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"❌ ส่งไม่สำเร็จ: {e}")

st.sidebar.markdown("## Company Report Portal")
menu = st.sidebar.selectbox("เมนูการใช้งาน", ["Generate Report", "System Log"])

if menu == "Generate Report":
    st.title("📊 Monthly Company Report Management")
    try:
        months = get_available_months()
        with open("companies.json", encoding="utf-8") as f: 
            email_map = json.load(f)
    except:
        months = []; email_map = {}
        st.error("❌ เชื่อมต่อข้อมูลไม่สำเร็จ หรือไฟล์ companies.json มีปัญหา")

    if not months: st.stop()
    month = st.selectbox("📅 เลือกเดือนที่ต้องการ", months)
    
    try: companies = get_companies_from_month(month)
    except: companies = []

    if not companies: st.stop()
    company = st.selectbox("🏢 เลือกบริษัท", companies)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 สร้างรายงานเฉพาะบริษัทนี้", use_container_width=True):
            with st.spinner("กำลังประมวลผล..."):
                files = fetch_company_files(company, month)
                if files:
                    _, final_report, zip_parts = process_files(files, company, month)
                    st.session_state["final_report"] = final_report
                    st.session_state["current_company"] = company
                    st.success("สร้างเสร็จสิ้น!")

    with col2:
        if st.button("🚀 เตรียมไฟล์ทุกบริษัท", use_container_width=True):
            with st.spinner("กำลังล้างไฟล์เก่าและเตรียมไฟล์ใหม่..."):
                st.session_state["prepared_list"] = run_all(month)
                st.success(f"✅ เตรียมไฟล์เสร็จสิ้น {len(st.session_state['prepared_list'])} บริษัท!")

    if "prepared_list" in st.session_state and st.session_state["prepared_list"]:
        st.info("💡 ไฟล์ในลิสต์ด้านล่างพร้อมส่งแล้ว")
        with st.expander("⚡️ เมนูส่งรวดเดียว", expanded=True):
            bulk_c1, bulk_c2 = st.columns([3, 1])
            bulk_email = bulk_c1.text_input("ระบุอีเมลผู้รับเดียว:", value="ITService0403@gmail.com")
            if bulk_c2.button("🚀 ส่งทั้งหมดรวดเดียว", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_txt = st.empty()
                items = st.session_state["prepared_list"]
                
                for idx, item in enumerate(items):
                    c_name = item['company']
                    r_path = item['report_path']
                    c_info, j_key = get_comp_config(c_name, email_map)
                    d_name = j_key if j_key else c_name
                    
                    status_txt.write(f"正在ส่ง ({idx+1}/{len(items)}): {d_name}...")
                    
                    m_en = get_month_en(month)
                    i_no = f"{datetime.datetime.now().strftime('%Y%m%d')}1028"
                    
                    try:
                        sub = c_info.get("subject", "รายงาน {month}").format(month=month, company=d_name, month_en=m_en)
                        msg = c_info.get("body", "ส่งไฟล์รายงานจ้า").format(month=month, company=d_name, month_en=m_en, issue_no=i_no)
                    except KeyError as e:
                        st.error(f"❌ ข้อมูลใน JSON สำหรับ {d_name} ขาดตัวแปร: {e}")
                        continue

                    try:
                        tmb_files = glob.glob(os.path.join("output", f"*{c_name}*PART*.7z"))
                        send_files = sorted(tmb_files) if tmb_files else [r_path]
                        send_email(bulk_email, send_files, subject=sub, body=msg)
                        time.sleep(1.2)
                    except Exception as e:
                        st.error(f"Error {c_name}: {e}")
                    
                    progress_bar.progress((idx + 1) / len(items))
                
                status_txt.success("✨ ส่งรวดเดียวครบทุกบริษัทแล้ว!")
                st.balloons()

    if "prepared_list" in st.session_state and st.session_state["prepared_list"]:
        st.divider()
        st.subheader("📩 รายการคัดกรองจาก Config")
        for item in st.session_state["prepared_list"]:
            c_name = item['company']
            r_path = item['report_path']
            
            c_info, j_key = get_comp_config(c_name, email_map)
            if not j_key: continue

            row_c, row_s, row_b = st.columns([3, 1, 1])
            row_c.write(f"🏢 **{j_key}**")
            
            if os.path.exists(r_path) or "TMB_TRUE" in c_name.upper():
                row_s.write("✅ Ready")
                if row_b.button("จัดการ", key=f"btn_{c_name}"):
                    tmb_fs = glob.glob(os.path.join("output", f"*{c_name}*PART*.7z"))
                    send_email_dialog(c_name, tmb_fs if tmb_fs else [r_path], month, email_map)
            else: row_s.error("ไฟล์หาย")

elif menu == "System Log":
    st.title("🖥 System Log")
    log_file = "logs/system.log"
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f: 
            st.code("".join(f.readlines()[-100:]))