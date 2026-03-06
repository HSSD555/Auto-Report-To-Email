import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

def send_email(receiver_email, file_paths):

    msg = EmailMessage()

    msg["Subject"] = "Monthly Company Reports (Categorized)"
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email

    msg.set_content(
        "Hello,\n\nPlease find the attached categorized reports for this month.\n\nBest regards,\nAutomated System"
    )

    for path in file_paths:
        with open(path, "rb") as f:
            data = f.read()
            filename = os.path.basename(path)

        msg.add_attachment(
            data,
            maintype="application",
            subtype="pdf",
            filename=filename
        )

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

    print(f"Email sent successfully with {len(file_paths)} attachments")