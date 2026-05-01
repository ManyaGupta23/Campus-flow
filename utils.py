import pandas as pd
import os
import shutil
import datetime
from fpdf import FPDF

FILE = "campus_pro.xlsx"

# ---------------- LOAD SHEET ----------------
def load_sheet(sheet, columns):
    if not os.path.exists(FILE):
        return pd.DataFrame(columns=columns)

    try:
        return pd.read_excel(FILE, sheet_name=sheet)
    except:
        return pd.DataFrame(columns=columns)

# ---------------- SAVE SHEET ----------------
def save_sheet(sheet, df):
    if os.path.exists(FILE):
        try:
            old = pd.read_excel(FILE, sheet_name=sheet)
            df = pd.concat([old, df], ignore_index=True)
        except:
            pass

    with pd.ExcelWriter(FILE, engine="openpyxl",
                        mode="a" if os.path.exists(FILE) else "w",
                        if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=sheet, index=False)

# ---------------- BACKUP SYSTEM ----------------
def backup_excel():
    if os.path.exists(FILE):
        os.makedirs("backup", exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        shutil.copy(FILE, f"backup/backup_{timestamp}.xlsx")

# ---------------- CERTIFICATE GENERATOR ----------------
def generate_certificate(name, roll, course):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", 'B', 18)
    pdf.cell(200, 10, "CERTIFICATE OF COMPLETION", ln=True, align="C")

    pdf.ln(20)
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, f"This is to certify that {name}", ln=True)
    pdf.cell(200, 10, f"Roll Number: {roll}", ln=True)
    pdf.cell(200, 10, f"has successfully completed {course}", ln=True)

    pdf.ln(15)
    pdf.cell(200, 10, "Campus Flow Pro - MCA Project", ln=True, align="C")

    filename = f"{roll}_certificate.pdf"
    pdf.output(filename)

    return filename