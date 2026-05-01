import streamlit as st
import pandas as pd 
import os 
from datetime import datetime 
import plotly.express as px 
from reportlab.pdfgen import canvas

======================================

SMART CAMPUS ERP SYSTEM (MCA LEVEL)

Admin + Teacher + Student Panel

Excel Backend + PDF + Backup + Analytics

======================================

EXCEL_FILE = "campus.xlsx" BACKUP_FOLDER = "backups"

-----------------------------

PAGE CONFIG

-----------------------------

st.set_page_config( page_title="Smart Campus ERP", page_icon="🏫", layout="wide" )

-----------------------------

PREMIUM UI STYLE

-----------------------------

st.markdown("""

<style>
.main {
    background-color: #f7fbff;
}
h1, h2, h3 {
    color: #0d47a1;
}
.stButton > button {
    border-radius: 10px;
    height: 3em;
    width: 100%;
}
</style>""", unsafe_allow_html=True)

-----------------------------

DEFAULT SHEETS

-----------------------------

DEFAULT_SHEETS = { "Students": ["Name", "Roll", "Course", "Semester", "Email", "Phone"], "Faculty": ["FacultyName", "Subject", "Department"], "Results": ["Roll", "Subject", "Marks", "Grade"], "Attendance": ["Roll", "Subject", "Present", "Total", "Percentage"], "Fees": ["Roll", "AmountPaid", "PendingFees", "Date"], "Users": ["Username", "Password", "Role"] }

-----------------------------

INIT EXCEL

-----------------------------

def init_excel(): if not os.path.exists(EXCEL_FILE): with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer: for sheet, cols in DEFAULT_SHEETS.items(): pd.DataFrame(columns=cols).to_excel(writer, sheet_name=sheet, index=False)

-----------------------------

LOAD SHEET

-----------------------------

def load_sheet(sheet): try: return pd.read_excel(EXCEL_FILE, sheet_name=sheet) except: return pd.DataFrame(columns=DEFAULT_SHEETS[sheet])

-----------------------------

SAVE SHEET

-----------------------------

def save_sheet(sheet, df): all_data = {} for s in DEFAULT_SHEETS: if s == sheet: all_data[s] = df else: all_data[s] = load_sheet(s)

with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
    for s, data in all_data.items():
        data.to_excel(writer, sheet_name=s, index=False)

-----------------------------

BACKUP SYSTEM

-----------------------------

def backup_excel(): os.makedirs(BACKUP_FOLDER, exist_ok=True) timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") backup_file = f"{BACKUP_FOLDER}/backup_{timestamp}.xlsx"

if os.path.exists(EXCEL_FILE):
    import shutil
    shutil.copy(EXCEL_FILE, backup_file)
    return backup_file
return None

-----------------------------

PDF CERTIFICATE

-----------------------------

def generate_certificate(name, roll, course): filename = f"certificate_{roll}.pdf" c = canvas.Canvas(filename) c.setFont("Helvetica-Bold", 18) c.drawString(180, 780, "CERTIFICATE OF ACHIEVEMENT")

c.setFont("Helvetica", 12)
c.drawString(100, 700, f"This is to certify that {name}")
c.drawString(100, 675, f"Roll Number: {roll}")
c.drawString(100, 650, f"Course: {course}")
c.drawString(100, 625, "has successfully completed academic requirements.")

c.save()
return filename

-----------------------------

LOGIN SESSION

-----------------------------

init_excel()

if "login" not in st.session_state: st.session_state.login = False

if "role" not in st.session_state: st.session_state.role = ""

-----------------------------

LOGIN PAGE

-----------------------------

if not st.session_state.login: st.title("🏫 Smart Campus ERP Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")
role = st.selectbox("Login As", ["Admin", "Teacher", "Student"])

if st.button("Login"):
    st.session_state.login = True
    st.session_state.user = username
    st.session_state.role = role
    st.rerun()

-----------------------------

MAIN DASHBOARD

-----------------------------

else: st.sidebar.title("🏫 Smart Campus ERP") st.sidebar.write(f"User: {st.session_state.user}") st.sidebar.write(f"Role: {st.session_state.role}")

menu = st.sidebar.radio("Navigation", [
    "Dashboard",
    "Student Management",
    "Faculty Module",
    "Results",
    "Attendance",
    "Fee Management",
    "Analytics",
    "Certificate Generator",
    "Backup System",
    "Logout"
])

if menu == "Dashboard":
    st.title("📊 Dashboard")
    students = load_sheet("Students")
    faculty = load_sheet("Faculty")
    results = load_sheet("Results")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Students", len(students))
    c2.metric("Faculty Members", len(faculty))
    c3.metric("Results Entries", len(results))

elif menu == "Student Management":
    st.title("👨‍🎓 Student Management")

    name = st.text_input("Name")
    roll = st.text_input("Roll")
    course = st.selectbox("Course", ["BCA", "MCA", "BBA", "MBA"])
    semester = st.number_input("Semester", 1, 8)
    email = st.text_input("Email")
    phone = st.text_input("Phone")

    if st.button("Add Student"):
        df = load_sheet("Students")
        df.loc[len(df)] = [name, roll, course, semester, email, phone]
        save_sheet("Students", df)
        st.success("Student Added Successfully")

    st.dataframe(load_sheet("Students"))

elif menu == "Faculty Module":
    st.title("👨‍🏫 Faculty Module")

    fname = st.text_input("Faculty Name")
    subject = st.text_input("Subject")
    dept = st.text_input("Department")

    if st.button("Add Faculty"):
        df = load_sheet("Faculty")
        df.loc[len(df)] = [fname, subject, dept]
        save_sheet("Faculty", df)
        st.success("Faculty Added")

    st.dataframe(load_sheet("Faculty"))

elif menu == "Fee Management":
    st.title("💰 Fee Management")

    roll = st.text_input("Student Roll")
    paid = st.number_input("Amount Paid", 0)
    pending = st.number_input("Pending Fees", 0)

    if st.button("Save Fee"):
        df = load_sheet("Fees")
        df.loc[len(df)] = [roll, paid, pending, str(datetime.now().date())]
        save_sheet("Fees", df)
        st.success("Fee Updated")

    st.dataframe(load_sheet("Fees"))

elif menu == "Analytics":
    st.title("📈 Analytics")
    df = load_sheet("Results")

    if not df.empty:
        fig = px.bar(df, x="Subject", y="Marks", color="Subject")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No analytics data available")

elif menu == "Certificate Generator":
    st.title("🏆 Certificate Generator")

    name = st.text_input("Student Name")
    roll = st.text_input("Roll Number")
    course = st.text_input("Course")

    if st.button("Generate Certificate"):
        file = generate_certificate(name, roll, course)
        with open(file, "rb") as f:
            st.download_button("Download Certificate", f, file_name=file)

elif menu == "Backup System":
    st.title("💾 Backup System")

    if st.button("Create Backup"):
        file = backup_excel()
        if file:
            st.success(f"Backup Created: {file}")

elif menu == "Logout":
    st.session_state.login = False
    st.rerun()
