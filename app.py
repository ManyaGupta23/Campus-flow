import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import base64

# -----------------------------
# 1. Page Configuration & Theme
# -----------------------------
st.set_page_config(page_title="Campus Flow Pro", page_icon="🏫", layout="wide")

# Premium Light Theme with Blue Accents (Inspired by your image)
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; color: #1E293B; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E2E8F0; }
    .main-header { color: #1E3A8A; font-weight: 800; font-size: 3rem; margin-bottom: 0; }
    .stButton>button { background-color: #2563EB; color: white; border-radius: 8px; width: 100%; border: none; }
    .stMetric { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border: 1px solid #E2E8F0; }
    .glass-card { background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(10px); border-radius: 15px; padding: 20px; border: 1px solid rgba(255, 255, 255, 0.3); }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 2. Database & PDF Logic
# -----------------------------
EXCEL_FILE = "campus_pro.xlsx"

def load_sheet(sheet_name, columns):
    if os.path.exists(EXCEL_FILE):
        try: return pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
        except: return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_sheet(sheet_name, new_data, columns):
    old_data = load_sheet(sheet_name, columns)
    final_data = pd.concat([old_data, new_data], ignore_index=True)
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a" if os.path.exists(EXCEL_FILE) else "w", if_sheet_exists="replace" if os.path.exists(EXCEL_FILE) else None) as writer:
        final_data.to_excel(writer, sheet_name=sheet_name, index=False)

def create_pdf(name, roll, course, marks_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="CAMPUS FLOW - ACADEMIC REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Student Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Roll Number: {roll}", ln=True)
    pdf.cell(200, 10, txt=f"Course: {course}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt="Performance Summary:", ln=True)
    for index, row in marks_df.iterrows():
        pdf.cell(200, 10, txt=f"{row['Subject']}: {row['Marks']}/100", ln=True)
    return pdf.output(dest="S").encode("latin-1")

# -----------------------------
# 3. Login & Authentication
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.image("college_building.jpeg", use_container_width=True, caption="Welcome to the Digital Library Portal")
    with col2:
        st.markdown("<h1 style='color: #1E3A8A;'>Portal Login</h1>", unsafe_allow_html=True)
        u_name = st.text_input("Username")
        u_pass = st.text_input("Password", type="password")
        role = st.selectbox("I am a...", ["Admin", "Teacher", "Student"])
        if st.button("Access Portal"):
            if u_pass == "admin123": # Simplified for demo
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.username = u_name
                st.rerun()
            else: st.error("Invalid Credentials")

# -----------------------------
# 4. Main Application
# -----------------------------
else:
    role = st.session_state.role
    st.sidebar.markdown(f"### 🛡️ {role} Account")
    st.sidebar.write(f"User: {st.session_state.username}")
    
    menu_options = ["Dashboard"]
    if role == "Admin": menu_options += ["Student Registration", "Faculty Management"]
    if role in ["Admin", "Teacher"]: menu_options += ["Attendance", "Exam Results", "Performance Predictor"]
    if role == "Student": menu_options += ["My Report Card"]
    
    menu = st.sidebar.radio("Navigate System", menu_options)
    if st.sidebar.button("Secure Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- DASHBOARD (Universal) ---
    if menu == "Dashboard":
        st.markdown(f"<p class='main-header'>Welcome to Campus Flow</p>", unsafe_allow_html=True)
        df_s = load_sheet("Students", ["Name", "Roll", "Course", "Semester"])
        df_r = load_sheet("Results", ["Roll", "Subject", "Marks"])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Students", len(df_s))
        c2.metric("Avg Campus Score", f"{df_r['Marks'].mean():.1f}" if not df_r.empty else "N/A")
        c3.metric("System Status", "Live")

        if not df_r.empty:
            st.subheader("📊 Subject-wise Comparison")
            fig = px.box(df_r, x="Subject", y="Marks", points="all", color="Subject", title="Marks Distribution Across Subjects")
            st.plotly_chart(fig, use_container_width=True)

    # --- ADMIN: REGISTRATION ---
    elif menu == "Student Registration":
        st.header("📋 Direct Enrollment")
        with st.form("reg_form"):
            n = st.text_input("Student Full Name")
            r = st.text_input("Unique Roll Number")
            c = st.selectbox("Course", ["BCA", "MCA", "BBA", "MBA"])
            if st.form_submit_button("Save to Excel"):
                save_sheet("Students", pd.DataFrame([[n, r, c, 1]], columns=["Name", "Roll", "Course", "Semester"]), ["Name", "Roll", "Course", "Semester"])
                st.success(f"Data for {n} written to campus_pro.xlsx")

    # --- TEACHER: PREDICTOR ---
    elif menu == "Performance Predictor":
        st.header("🤖 AI Student Analytics")
        df_r = load_sheet("Results", ["Roll", "Subject", "Marks"])
        if not df_r.empty:
            selected_roll = st.selectbox("Select Student Roll to Predict Performance", df_r['Roll'].unique())
            student_data = df_r[df_r['Roll'] == selected_roll]
            avg_score = student_data['Marks'].mean()
            
            st.markdown(f"<div class='glass-card'><h3>Prediction for {selected_roll}</h3>", unsafe_allow_html=True)
            if avg_score > 75: 
                st.success("Result: High Probability of Distinction")
                st.info("Recommendation: Fast-track for placement training.")
            elif avg_score > 50:
                st.warning("Result: Average Performance")
                st.info("Recommendation: Needs consistent mock tests.")
            else:
                st.error("Result: High Risk of Backlog")
                st.info("Recommendation: Schedule remedial classes immediately.")
            st.markdown("</div>", unsafe_allow_html=True)
        else: st.info("Need more exam data to run predictions.")

    # --- STUDENT: REPORT CARD ---
    elif menu == "My Report Card":
        st.header("📜 Academic Download")
        roll = st.text_input("Verify Your Roll Number")
        if st.button("Generate PDF"):
            df_s = load_sheet("Students", ["Name", "Roll", "Course", "Semester"])
            df_r = load_sheet("Results", ["Roll", "Subject", "Marks"])
            student_info = df_s[df_s['Roll'] == roll]
            marks_info = df_r[df_r['Roll'] == roll]
            
            if not student_info.empty:
                pdf_data = create_pdf(student_info.iloc[0]['Name'], roll, student_info.iloc[0]['Course'], marks_info)
                b64 = base64.b64encode(pdf_data).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="Report_{roll}.pdf">Click here to Download PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("Report Card Generated!")
            else: st.error("Roll Number not found.")
