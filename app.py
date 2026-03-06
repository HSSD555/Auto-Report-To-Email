import streamlit as st
import json
import pandas as pd
import os
from automation import process_files
from send_mail import send_email
from database import get_zip_files
from logger import log

st.set_page_config(
    page_title="Company Report Portal",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>

.main-title{
font-size:36px;
font-weight:bold;
color:#1f4e79;
margin-bottom:20px;
}

.card{
background:#ffffff;
padding:20px;
border-radius:12px;
box-shadow:0px 4px 10px rgba(0,0,0,0.1);
margin-bottom:15px;
}

</style>
""", unsafe_allow_html=True)

with open("companies.json") as f:
    companies = json.load(f)

st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
    width=80
)

st.sidebar.markdown("## Company Portal")

menu = st.sidebar.selectbox(
    "Menu",
    ["Generate Report", "Report History", "System Log"],
    key="menu_select"
)

if menu == "Generate Report":

    st.markdown(
        '<div class="main-title">📊 Monthly Company Report</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        company = st.selectbox(
            "🏢 Select Company",
            list(companies.keys()),
            key="company_select"
        )

    with col2:

        month = st.selectbox(
            "📅 Select Month",
            [
                "January","February","March","April","May","June",
                "July","August","September","October","November","December"
            ],
            key="month_select"
        )

    st.write("")

    if st.button("📄 Generate Report", key="generate_btn"):

        with st.spinner("Generating categorized reports..."):

            files = get_zip_files(company, month)

            if not files:
                st.warning(f"No zip files found for {company} in {month}.")
            else:
                pdfs = process_files(files, company, month)

                st.session_state["pdf_paths"] = pdfs

                st.success(f"Report Generated Successfully ({len(pdfs)} categories found)")
                log(f"generate report {company} {month}")

    if "pdf_paths" in st.session_state:

        st.write("### 📁 Generated Files:")

        for pdf_path in st.session_state["pdf_paths"]:
            with open(pdf_path, "rb") as f:
                filename = os.path.basename(pdf_path)
                st.download_button(
                    label=f"⬇ Download {filename}",
                    data=f,
                    file_name=filename,
                    key=f"download_{filename}"
                )

    st.write("")

    if st.button("✉ Send Email", key="send_email_btn"):

        if "pdf_paths" not in st.session_state:

            st.error("Please generate report first")

        else:

            email = companies[company]

            pdfs = st.session_state["pdf_paths"]

            send_email(email, pdfs)

            st.success("Email Sent Successfully with all attachments")

            log(f"email sent {company} {month} (Categorized)")

            st.write("")
            
    st.divider()

    st.subheader("⚡ Auto Generate All Reports")

    if st.button("🚀 Generate ALL Reports (All Companies / All Months)"):

        months = [
            "January","February","March","April","May","June",
            "July","August","September","October","November","December"
        ]

        total_jobs = len(companies) * len(months)
        progress = st.progress(0)

        job = 0

        for company_name, email in companies.items():

            for m in months:

                try:

                    files = get_zip_files(company_name, m)

                    if not files:
                        log(f"skip {company_name} {m} no files")
                    else:
                        pdfs = process_files(files, company_name, m)

                        send_email(email, pdfs)

                        log(f"success {company_name} {m}")

                except Exception as e:

                    log(f"error {company_name} {m} {str(e)}")

                job += 1
                progress.progress(job / total_jobs)

        st.success("🎉 All Reports Generated & Sent")

elif menu == "Report History":

    st.markdown(
        '<div class="main-title">📁 Report History</div>',
        unsafe_allow_html=True
    )

    data = {
        "Company":["CompanyA","CompanyB","CompanyC"],
        "Month":["Jan","Feb","Mar"],
        "Year":["2025","2025","2025"],
        "Status":["Generated","Sent","Generated"]
    }

    df = pd.DataFrame(data)

    st.dataframe(df, use_container_width=True)

elif menu == "System Log":

    st.markdown(
        '<div class="main-title">🖥 System Log</div>',
        unsafe_allow_html=True
    )

    try:

        with open("logs/system.log") as f:
            logs = f.readlines()

        for l in logs[-30:]:
            st.text(l)

    except:
        st.info("No logs found")