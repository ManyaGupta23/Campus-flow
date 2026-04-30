import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px
from fpdf import FPDF
import base64

# -----------------------------
# 1. Page Configuration & Premium Theme
# -----------------------------
st.set_page_config(page_title="Campus Flow Pro", page_icon="🏫", layout="wide")

# White & Blue Premium Professional UI
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; color: #1E293B; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E2E8F0; }
    .main-header { color: #1E3A8A; font-weight: 800; font-size: 2.5rem; margin-bottom: 0; }
    .stButton>button { background-color: #2563EB; color: white; border-radius: 8px; border: none; height: 3em; }
    .stMetric { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border: 1px solid #E2E8F0; }
    .glass-card { background: white; padding: 25px; border-radius: 15px; border: 1px solid #E2E8F0; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 2. Database & PDF Logic
# -----------------------------
EXCEL_FILE = "campus.xlsx"

def load_sheet(sheet_name, columns):
    if os.path.exists(EXCEL_FILE):
        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
            return df
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_sheet(sheet_name, new_data, columns):
    if not os.path.exists(EXCEL_FILE):
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            new_data.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        old_data = load_sheet(sheet_name, columns)
        final_data = pd.concat([old_data, new_data], ignore_index=True)
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            final_data.to_excel(writer, sheet_name=sheet_name, index=False)

def create_pdf(name, roll, course, marks_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(200, 20, txt="CAMPUS FLOW - ACADEMIC REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, txt=f"Student Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Roll Number: {roll}", ln=True)
    pdf.cell(200, 10, txt=f"Course: {course}", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt="Examination Results:", ln=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Subject", 1)
    pdf.cell(50, 10, "Marks", 1)
    pdf.ln()
    pdf.set_font("Arial", size=12)
    for index, row in marks_df.iterrows():
        pdf.cell(100, 10, str(row['Subject']), 1)
        pdf.cell(50, 10, str(row['Marks']), 1)
        pdf.ln()
    return pdf.output(dest="S").encode("latin-1")

# -----------------------------
# 3. Login System
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col_img, col_form = st.columns([1.5, 1])
    with col_img:
        st.image("college_building.jpeg", use_container_width=True)
    with col_form:
        st.markdown("<h1 style='color: #1E3A8A;'>Portal Login</h1>", unsafe_allow_html=True)
        u_name = st.text_input("Username")
        u_pass = st.text_input("Password", type="password")
        u_role = st.selectbox("Role", ["Admin", "Teacher", "Student"])
        if st.button("Login"):
            if u_pass == "admin123":
                st.session_state.logged_in = True
                st.session_state.role = u_role
                st.session_state.username = u_name
                st.rerun()
            else:
                st.error("Invalid password. (Try admin123)")

# -----------------------------
# 4. Main App
# -----------------------------
else:
    role = st.session_state.role
    st.sidebar.markdown(f"### 🛡️ {role} Account")
    
    # Navigation Logic
    nav_options = ["Dashboard"]
    if role == "Admin": nav_options += ["Student Registration", "Faculty Management"]
    if role in ["Admin", "Teacher"]: nav_options += ["Attendance", "Exam Results", "Performance Predictor"]
    if role == "Student": nav_options += ["My Report Card"]
    
    menu = st.sidebar.radio("Navigate", nav_options)
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown(f"<p class='main-header'>Campus Flow Pro</p>", unsafe_allow_html=True)
    st.caption(f"Logged in as {st.session_state.username} | Access Level: {role}")

    # --- DASHBOARD ---
    if menu == "Dashboard":
        df_s = load_sheet("Students", ["Name", "Roll", "Course", "Semester"])
        df_f = load_sheet("Faculty", ["Faculty Name", "Subject", "Department"])
        df_r = load_sheet("Results", ["Roll", "Subject", "Marks"])

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Students", len(df_s))
        c2.metric("Active Faculty", len(df_f))
        c3.metric("Avg Campus Score", f"{df_r['Marks'].mean():.1f}" if not df_r.empty else "0")

        if not df_s.empty:
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Enrollment Distribution")
                fig = px.pie(df_s, names='Course', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.subheader("Recent Activity")
                st.dataframe(df_s.tail(5), use_container_width=True)

    # --- STUDENT REGISTRATION ---
    elif menu == "Student Registration":
        st.header("📋 Register New Student")
        with st.form("reg_form"):
            n = st.text_input("Full Name")
            r = st.text_input("Roll Number")
            c = st.selectbox("Course", ["BCA", "MCA", "BBA", "MBA"])
            if st.form_submit_button("Save Student"):
                save_sheet("Students", pd.DataFrame([[n, r, c, 1]], columns=["Name", "Roll", "Course", "Semester"]), ["Name", "Roll", "Course", "Semester"])
                st.success("Registration Successful!")

    # --- FACULTY MANAGEMENT ---
    elif menu == "Faculty Management":
        st.header("👨‍🏫 Faculty Directory")
        with st.form("fac_form"):
            f_name = st.text_input("Faculty Name")
            sub = st.text_input("Specialization")
            dept = st.selectbox("Department", ["Computer Science", "Management", "Commerce"])
            if st.form_submit_button("Add Faculty"):
                save_sheet("Faculty", pd.DataFrame([[f_name, sub, dept]], columns=["Faculty Name", "Subject", "Department"]), ["Faculty Name", "Subject", "Department"])
                st.success("Faculty added!")
        st.dataframe(load_sheet("Faculty", ["Faculty Name", "Subject", "Department"]), use_container_width=True)

    # --- ATTENDANCE ---
    elif menu == "Attendance":
        st.header("📅 Daily Attendance")
        with st.form("att_form"):
            roll = st.text_input("Roll Number")
            status = st.radio("Status", ["Present", "Absent"], horizontal=True)
            if st.form_submit_button("Submit"):
                save_sheet("Attendance", pd.DataFrame([[roll, date.today(), status]], columns=["Roll", "Date", "Status"]), ["Roll", "Date", "Status"])
                st.success("Attendance Marked!")

    # --- EXAM RESULTS ---
    elif menu == "Exam Results":
        st.header("📝 Result Entry")
        with st.form("res_form"):
            res_roll = st.text_input("Roll Number")
            sub_name = st.text_input("Subject")
            score = st.number_input("Marks", 0, 100)
            if st.form_submit_button("Save"):
                save_sheet("Results", pd.DataFrame([[res_roll, sub_name, score]], columns=["Roll", "Subject", "Marks"]), ["Roll", "Subject", "Marks"])
                st.success("Marks Saved!")

    # --- PERFORMANCE PREDICTOR ---
    elif menu == "Performance Predictor":
        st.header("🤖 AI Performance Predictor")
        df_r = load_sheet("Results", ["Roll", "Subject", "Marks"])
        if not df_r.empty:
            sel_roll = st.selectbox("Select Student", df_r['Roll'].unique())
            avg = df_r[df_r['Roll'] == sel_roll]['Marks'].mean()
            st.markdown(f"<div class='glass-card'><h3>Analysis for: {sel_roll}</h3>", unsafe_allow_html=True)
            if avg > 75: st.success("Result: Distinction Likely")
            elif avg > 40: st.warning("Result: Average Performance")
            else: st.error("Result: Remedial Needed")
            st.markdown("</div>", unsafe_allow_html=True)
        else: st.info("Input Exam Results first.")

    # --- MY REPORT CARD ---
    elif menu == "My Report Card":
        st.header("📜 Download Report Card")
        roll_in = st.text_input("Verify Roll Number")
        if st.button("Generate PDF"):
            df_s = load_sheet("Students", ["Name", "Roll", "Course", "Semester"])
            df_r = load_sheet("Results", ["Roll", "Subject", "Marks"])
            student = df_s[df_s['Roll'] == roll_in]
            results = df_r[df_r['Roll'] == roll_in]
            if not student.empty:
                pdf_bytes = create_pdf(student.iloc[0]['Name'], roll_in, student.iloc[0]['Course'], results)
                st.download_button("Download Now", pdf_bytes, f"Report_{roll_in}.pdf", "application/pdf")
            else: st.error("Roll Number Not Found.")
