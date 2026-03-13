import smtplib
import os
import zipfile
import time
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from email.header import Header
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465 
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

def send_email(receiver_email, file_paths, subject=None, body=None, force_zip=False):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        raise Exception("ไม่พบข้อมูลการตั้งค่า Email")

    temp_files_to_clean = []
    final_attach_paths = []
    
    FILE_SIZE_LIMIT = 20 * 1024 * 1024 

    try:
        if isinstance(file_paths, str): file_paths = [file_paths]

        for f in file_paths:
            if not os.path.exists(f): 
                print(f"⚠️ Warning: ไม่พบไฟล์ที่จะแนบ: {f}")
                continue
            
            f_size = os.path.getsize(f)
            f_lower = f.lower()
            
            is_already_compressed = (
                f_lower.endswith(".zip") or 
                f_lower.endswith(".7z") or 
                ".7z." in f_lower or 
                "_part" in f_lower
            )
            
            if (not is_already_compressed) and (f_size > FILE_SIZE_LIMIT or force_zip):
                timestamp = time.time_ns()
                zip_name = f.replace(".pdf", f"_{timestamp}.zip")
                
                print(f"📦 Auto-Zipping large PDF: {os.path.basename(f)}")
                with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(f, os.path.basename(f))
                
                final_attach_paths.append(zip_name)
                temp_files_to_clean.append(zip_name)
            else:
                final_attach_paths.append(f)

        msg = MIMEMultipart()
        msg["Subject"] = Header(subject or "Monthly Report Submission", "utf-8")
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email
        
        msg.attach(MIMEText(body or "", "plain", "utf-8"))

        for path in final_attach_paths:
            try:
                filename = os.path.basename(path)
                print(f"📎 Attaching: {filename}")
                with open(path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                
                part.add_header(
                    "Content-Disposition", 
                    f"attachment; filename=\"{Header(filename, 'utf-8').encode()}\""
                )
                msg.attach(part)
            except Exception as e:
                print(f"❌ Error attaching file {path}: {e}")

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=300) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            
        print(f"🚀 Email sent successfully to {receiver_email} (Total files: {len(final_attach_paths)})")
        return True

    except Exception as e:
        print(f"❌ SMTP Error: {e}")
        raise e

    finally:
        for tmp in temp_files_to_clean:
            if os.path.exists(tmp):
                try: 
                    os.remove(tmp)
                    print(f"🧹 Cleaned up temp file: {tmp}")
                except: pass