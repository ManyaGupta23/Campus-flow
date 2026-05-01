import streamlit as st
import pandas as pd
import os
import shutil
from datetime import datetime
import plotly.express as px
from reportlab.pdfgen import canvas

# -----------------------------
# CONSTANTS & CONFIG
# -----------------------------
EXCEL_FILE = "campus.xlsx"
BACKUP_FOLDER = "backups"

st.set_page_config(page_title="Smart Campus ERP", page_icon="🏫", layout="wide")

# Premium UI Style
st.markdown("""
<style>
    .main { background-color: #f7fbff; }
    h1, h2, h3 { color: #0d47a1; }
    .stButton > button { border-radius: 10px; height: 3em; width: 100%; background-color: #0d47a1; color: white; }
</style>
""", unsafe_allow_html=True)

DEFAULT_SHEETS = {
    "Students": ["Name", "Roll", "Course", "Semester", "Email", "Phone"],
    "Faculty": ["FacultyName", "Subject", "Department"],
    "Results": ["Roll", "Subject", "Marks", "Grade"],
    "Attendance": ["Roll", "Subject", "Present", "Total", "Percentage"],
    "Fees": ["Roll", "AmountPaid", "PendingFees", "Date"],
    "Users": ["Username", "Password", "Role"]
}

# -----------------------------
# DATABASE FUNCTIONS
# -----------------------------
def init_excel():
    if not os.path.exists(EXCEL_FILE):
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            for sheet, cols in DEFAULT_SHEETS.items():
                pd.DataFrame(columns=cols).to_excel(writer, sheet_name=sheet, index=False)

def load_sheet(sheet):
    try:
        return pd.read_excel(EXCEL_FILE, sheet_name=sheet)
    except Exception:
        return pd.DataFrame(columns=DEFAULT_SHEETS[sheet])

def save_sheet(sheet, df):
    # Load all sheets to ensure we don't lose other data when writing
    all_sheets = {s: load_sheet(s) for s in DEFAULT_SHEETS.keys()}
    all_sheets[sheet] = df
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
        for s_name, s_df in all_sheets.items():
            s_df.to_excel(writer, sheet_name=s_name, index=False)

def backup_excel():
    os.makedirs(BACKUP_FOLDER, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{BACKUP_FOLDER}/backup_{ts}.xlsx"
    if os.path.exists(EXCEL_FILE):
        shutil.copy(EXCEL_FILE, backup_file)
        return backup_file
    return None

# -----------------------------
# AUTHENTICATION SESSION
# -----------------------------
init_excel()

if "login" not in st.session_state:
    st.session_state.login = False

# -----------------------------
# LOGIN PAGE
# -----------------------------
if not st.session_state.login:
    st.title("🏫 Smart Campus ERP Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Login As", ["Admin", "Teacher", "Student"])

    if st.button("Login"):
        # For academic projects, a simple session state logic is used
        # In production, check against the 'Users' sheet
        st.session_state.login = True
        st.session_state.user = username
        st.session_state.role = role
        st.rerun()

# -----------------------------
# MAIN DASHBOARD SYSTEM
# -----------------------------
else:
    role = st.session_state.role
    st.sidebar.title("🏫 Smart Campus ERP")
    st.sidebar.write(f"**User:** {st.session_state.user}")
    st.sidebar.write(f"**Role:** {role}")

    # Role-Based Navigation
    menu_options = ["Dashboard", "Attendance", "Results", "Analytics", "Certificate Generator", "Logout"]
    if role in ["Admin", "Teacher"]:
        menu_options.insert(1, "Student Management")
        menu_options.insert(2, "Faculty Module")
    if role == "Admin":
        menu_options.insert(6, "Fee Management")
        menu_options.insert(8, "Backup System")

    menu = st.sidebar.radio("Navigation", menu_options)

    # 1. DASHBOARD
    if menu == "Dashboard":
        st.title("📊 System Overview")
        c1, c2, c3 = st.columns(3)
        c1.metric("Students", len(load_sheet("Students")))
        c2.metric("Faculty", len(load_sheet("Faculty")))
        c3.metric("Results Processed", len(load_sheet("Results")))
        st.divider()
        st.subheader("System Status: Active ✅")

    # 2. STUDENT MANAGEMENT
    elif menu == "Student Management":
        st.title("👨‍🎓 Student Management")
        df = load_sheet("Students")
        
        tab1, tab2 = st.tabs(["Add Student", "View & Search"])
        with tab1:
            with st.form("add_student"):
                name = st.text_input("Name")
                roll = st.text_input("Roll")
                course = st.selectbox("Course", ["BCA", "MCA", "BBA", "MBA"])
                sem = st.number_input("Semester", 1, 8)
                email = st.text_input("Email")
                phone = st.text_input("Phone")
                if st.form_submit_button("Add Student"):
                    new_row = pd.DataFrame([[name, roll, course, sem, email, phone]], columns=df.columns)
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_sheet("Students", df)
                    st.success("Student Added Successfully")
        with tab2:
            search = st.text_input("Search by Roll Number")
            if search:
                st.dataframe(df[df['Roll'].astype(str).str.contains(search)])
            else:
                st.dataframe(df)

    # 3. FACULTY MODULE
    elif menu == "Faculty Module":
        st.title("👨‍🏫 Faculty Directory")
        f_df = load_sheet("Faculty")
        with st.form("add_faculty"):
            fname = st.text_input("Faculty Name")
            subject = st.text_input("Subject")
            dept = st.text_input("Department")
            if st.form_submit_button("Add Faculty"):
                new_row = pd.DataFrame([[fname, subject, dept]], columns=f_df.columns)
                f_df = pd.concat([f_df, new_row], ignore_index=True)
                save_sheet("Faculty", f_df)
                st.success("Faculty Added")
        st.dataframe(f_df)

    # 4. RESULTS
    elif menu == "Results":
        st.title("📘 Results Management")
        r_df = load_sheet("Results")
        with st.form("res_form"):
            roll = st.text_input("Roll Number")
            subj = st.text_input("Subject")
            marks = st.number_input("Marks", 0, 100)
            if st.form_submit_button("Save Result"):
                grade = "A" if marks >= 80 else "B" if marks >= 60 else "C" if marks >= 40 else "Fail"
                new_row = pd.DataFrame([[roll, subj, marks, grade]], columns=r_df.columns)
                r_df = pd.concat([r_df, new_row], ignore_index=True)
                save_sheet("Results", r_df)
                st.success(f"Result Saved with Grade: {grade}")
        st.dataframe(r_df)

    # 5. ATTENDANCE
    elif menu == "Attendance":
        st.title("📅 Attendance Management")
        a_df = load_sheet("Attendance")
        with st.form("att_form"):
            roll = st.text_input("Student Roll")
            subj = st.text_input("Subject Name")
            pres = st.number_input("Classes Attended", 0)
            tot = st.number_input("Total Classes", 1)
            if st.form_submit_button("Update Attendance"):
                perc = round((pres/tot)*100, 2)
                new_row = pd.DataFrame([[roll, subj, pres, tot, perc]], columns=a_df.columns)
                a_df = pd.concat([a_df, new_row], ignore_index=True)
                save_sheet("Attendance", a_df)
                st.success(f"Attendance Recorded: {perc}%")
        st.dataframe(a_df)

    # 6. FEE MANAGEMENT
    elif menu == "Fee Management":
        st.title("💰 Finance Module")
        fee_df = load_sheet("Fees")
        roll = st.text_input("Roll Number")
        paid = st.number_input("Amount Paid", 0)
        pending = st.number_input("Pending Fees", 0)
        if st.button("Save Fee Record"):
            new_row = pd.DataFrame([[roll, paid, pending, str(datetime.now().date())]], columns=fee_df.columns)
            fee_df = pd.concat([fee_df, new_row], ignore_index=True)
            save_sheet("Fees", fee_df)
            st.success("Record Saved")
        st.dataframe(fee_df)

    # 7. ANALYTICS
    elif menu == "Analytics":
        st.title("📈 Academic Analytics")
        res_data = load_sheet("Results")
        if not res_data.empty:
            fig = px.bar(res_data, x="Subject", y="Marks", color="Grade", title="Subject Performance")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for charts.")

    # 8. CERTIFICATE GENERATOR
    elif menu == "Certificate Generator":
        st.title("🏆 Certificate Center")
        s_name = st.text_input("Student Name")
        s_roll = st.text_input("Roll Number")
        s_course = st.text_input("Course")
        if st.button("Generate PDF"):
            fname = f"certificate_{s_roll}.pdf"
            c = canvas.Canvas(fname)
            c.setFont("Helvetica-Bold", 20)
            c.drawString(150, 780, "CERTIFICATE OF ACHIEVEMENT")
            c.setFont("Helvetica", 14)
            c.drawString(100, 700, f"This is to certify that {s_name}")
            c.drawString(100, 670, f"Roll Number: {s_roll} | Course: {s_course}")
            c.drawString(100, 640, "has completed the academic requirements successfully.")
            c.save()
            with open(fname, "rb") as f:
                st.download_button("Download Certificate", f, file_name=fname)

    # 9. BACKUP
    elif menu == "Backup System":
        st.title("💾 Data Maintenance")
        if st.button("Trigger Cloud Backup (Local)"):
            file = backup_excel()
            st.success(f"Backup created at: {file}")

    # 10. LOGOUT
    elif menu == "Logout":
        st.session_state.login = False
        st.rerun()
