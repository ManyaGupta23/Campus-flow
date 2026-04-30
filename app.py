import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px

# -----------------------------
# 1. Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Campus Flow - Smart Management",
    page_icon="🎓",
    layout="wide"
)

# -----------------------------
# 2. Professional Dark Theme UI
# -----------------------------
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; }
    section[data-testid="stSidebar"] { background-color: #161B22; }
    h1, h2, h3, h4, h5, h6, p, label { color: white; }
    .stMetric { background-color: #1E2329; padding: 15px; border-radius: 10px; border: 1px solid #30363D; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 3. Excel Database Logic
# -----------------------------
EXCEL_FILE = "campus.xlsx"

def load_sheet(sheet_name, columns):
    if os.path.exists(EXCEL_FILE):
        try:
            return pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_sheet(sheet_name, new_data, columns):
    # Load old data
    old_data = load_sheet(sheet_name, columns)
    final_data = pd.concat([old_data, new_data], ignore_index=True)
    
    # Handle multi-sheet writing
    if not os.path.exists(EXCEL_FILE):
        final_data.to_excel(EXCEL_FILE, sheet_name=sheet_name, index=False)
    else:
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            final_data.to_excel(writer, sheet_name=sheet_name, index=False)

# -----------------------------
# 4. Login System
# -----------------------------
users = {"admin": "admin123", "teacher": "teacher123", "student": "student123"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("🔐 Campus Flow Login")
    col_l, col_r = st.columns(2)
    with col_l:
        u_name = st.text_input("Username")
        u_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            if u_name in users and users[u_name] == u_pass:
                st.session_state.logged_in = True
                st.session_state.username = u_name
                st.rerun()
            else:
                st.error("Invalid credentials")

# -----------------------------
# 5. Main Application Logic
# -----------------------------
else:
    # Sidebar Navigation
    st.sidebar.title(f"Welcome, {st.session_state.username.capitalize()}")
    menu = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "Student Management", "Attendance", "Fees Management", "Faculty Management", "Exam Results"]
    )
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🎓 Campus Flow")
    st.caption("Centralized Smart College Management System")

    # --- MODULE: DASHBOARD ---
    if menu == "Dashboard":
        st.header("📊 Campus Analytics")
        
        # Load Data
        df_s = load_sheet("Students", ["Name", "Roll", "Course", "Semester"])
        df_f = load_sheet("Faculty", ["Faculty Name", "Subject", "Department"])
        df_fees = load_sheet("Fees", ["Student Name", "Amount", "Date"])

        # Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Students", len(df_s))
        m2.metric("Active Faculty", len(df_f))
        total_rev = df_fees["Amount"].sum() if not df_fees.empty else 0
        m3.metric("Fees Collected", f"₹{total_rev:,}")

        # Charts
        if not df_s.empty:
            st.markdown("---")
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.subheader("Student Enrollment by Course")
                fig = px.pie(df_s, names='Course', hole=0.4, template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            with col_chart2:
                st.subheader("Recent Activity")
                st.dataframe(df_s.tail(5), use_container_width=True)

    # --- MODULE: STUDENT MANAGEMENT ---
    elif menu == "Student Management":
        st.header("👨‍🎓 Student Registry")
        
        tab_add, tab_view = st.tabs(["Add New Student", "Search & Filter"])
        
        with tab_add:
            with st.form("add_student"):
                name = st.text_input("Full Name")
                roll = st.text_input("Roll Number")
                course = st.selectbox("Course", ["BCA", "MCA", "BBA", "MBA"])
                sem = st.slider("Semester", 1, 6)
                if st.form_submit_button("Register Student"):
                    new_df = pd.DataFrame([[name, roll, course, sem]], columns=["Name", "Roll", "Course", "Semester"])
                    save_sheet("Students", new_df, ["Name", "Roll", "Course", "Semester"])
                    st.success("Student registered successfully!")

        with tab_view:
            df_s = load_sheet("Students", ["Name", "Roll", "Course", "Semester"])
            search = st.text_input("Search by Name or Roll Number")
            if search:
                filtered = df_s[df_s['Name'].str.contains(search, case=False) | df_s['Roll'].astype(str).str.contains(search)]
                st.table(filtered)
            else:
                st.dataframe(df_s, use_container_width=True)

    # --- MODULE: ATTENDANCE ---
    elif menu == "Attendance":
        st.header("📅 Daily Attendance")
        with st.form("att_form"):
            roll = st.text_input("Enter Roll Number")
            status = st.radio("Status", ["Present", "Absent"], horizontal=True)
            if st.form_submit_button("Mark Attendance"):
                att_df = pd.DataFrame([[roll, date.today(), status]], columns=["Roll", "Date", "Status"])
                save_sheet("Attendance", att_df, ["Roll", "Date", "Status"])
                st.success(f"Attendance for {roll} recorded.")

    # --- MODULE: FEES ---
    elif menu == "Fees Management":
        st.header("💰 Fee Collection")
        with st.form("fee_form"):
            s_name = st.text_input("Student Name")
            amt = st.number_input("Amount Paid", min_value=0)
            if st.form_submit_button("Submit Record"):
                f_df = pd.DataFrame([[s_name, amt, date.today()]], columns=["Student Name", "Amount", "Date"])
                save_sheet("Fees", f_df, ["Student Name", "Amount", "Date"])
                st.success("Payment recorded.")

    # --- MODULE: FACULTY ---
    elif menu == "Faculty Management":
        st.header("👨‍🏫 Faculty Directory")
        with st.form("fac_form"):
            f_name = st.text_input("Name")
            sub = st.text_input("Specialization")
            dept = st.selectbox("Department", ["Computer Science", "Management", "Commerce"])
            if st.form_submit_button("Add Faculty"):
                fac_df = pd.DataFrame([[f_name, sub, dept]], columns=["Faculty Name", "Subject", "Department"])
                save_sheet("Faculty", fac_df, ["Faculty Name", "Subject", "Department"])
                st.success("Faculty member added.")

    # --- MODULE: EXAM RESULTS ---
    elif menu == "Exam Results":
        st.header("📝 Academic Performance")
        with st.form("res_form"):
            res_roll = st.text_input("Roll Number")
            sub_name = st.text_input("Subject Name")
            score = st.number_input("Marks Secured", 0, 100)
            if st.form_submit_button("Save Result"):
                res_df = pd.DataFrame([[res_roll, sub_name, score]], columns=["Student Name", "Subject", "Marks"])
                save_sheet("Results", res_df, ["Student Name", "Subject", "Marks"])
                st.success("Result synced to database.")