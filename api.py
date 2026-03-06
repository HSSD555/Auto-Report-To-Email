from fastapi import FastAPI
from pydantic import BaseModel
from automation import process_files
from send_mail import send_email

app = FastAPI()

# Model สำหรับรับ JSON
class ReportRequest(BaseModel):
    email: str


@app.get("/")
def home():
    return {"message": "Report API Running"}


@app.post("/generate-report")
def generate_report(data: ReportRequest):

    email = data.email

    # generate report
    pdf_file = process_files()

    # send email
    send_email(email, pdf_file)

    return {
        "status": "success",
        "message": "Report generated and sent",
        "email": email
    }