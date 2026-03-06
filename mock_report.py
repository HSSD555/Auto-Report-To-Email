from reportlab.pdfgen import canvas
import os

def create_mock_report(company, month):

    if not os.path.exists("output"):
        os.makedirs("output")

    file_path = f"output/{company}_{month}_report.pdf"

    c = canvas.Canvas(file_path)

    c.setFont("Helvetica", 20)
    c.drawString(200, 750, "Company Report")

    c.setFont("Helvetica", 14)
    c.drawString(200, 700, f"Company : {company}")
    c.drawString(200, 670, f"Month : {month}")

    c.drawString(200, 600, "Report Com")

    c.save()

    return file_path