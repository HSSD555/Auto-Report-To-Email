import smtplib
from email.message import EmailMessage
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = "Egm83054@gmail.com"
SENDER_PASSWORD = "fvzy zqyr fsjn nznm"

def send_email(receiver_email, file_path):

    msg = EmailMessage()

    msg["Subject"] = "Test Report"
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email

    msg.set_content(
        "This is a test report from the system."
    )

    # แนบไฟล์
    with open(file_path, "rb") as f:
        data = f.read()
        filename = os.path.basename(file_path)

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

    print("Email sent successfully")