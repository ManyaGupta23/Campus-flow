import streamlit as st
import pandas as pd
import plotly.express as px

from auth import login_user, register_user
from utils import load_sheet, save_sheet, backup_excel, generate_certificate

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Campus Flow Pro", layout="wide")

# ---------------- SESSION STATE ----------------
if "login" not in st.session_state:
    st.session_state.login = False

# =========================
# 🔐 LOGIN / REGISTER PAGE
# =========================
if not st.session_state.login:

    st.title("🏫 Campus Flow Pro - Secure Login")

    option = st.radio("Select Option", ["Login", "Register"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    role = "user"

    if option == "Register":
        role = st.selectbox("Role", ["Admin", "Teacher", "Student"])

        if st.button("Register"):
            if register_user(username, password, role):
                st.success("User Registered Successfully")
            else:
                st.error("User Already Exists")

    if option == "Login":
        if st.button("Login"):
            r = login_user(username, password)

            if r:
                st.session_state.login = True
                st.session_state.user = username
                st.session_state.role = r
                st.rerun()
            else:
                st.error("Invalid Credentials")

# =========================
# 🚀 MAIN SYSTEM
# =========================
else:

    st.sidebar.title("🏫 Campus Flow Pro")
    st.sidebar.write("User:", st.session_state.user)
    st.sidebar.write("Role:", st.session_state.role)

    menu = st.sidebar.radio("Navigation", [
        "Dashboard",
        "Student Management",
        "Results Management",
        "Attendance",
        "Analytics",
        "Certificate Generator",
        "Backup System",
        "Logout"
    ])

    # ---------------- DASHBOARD ----------------
    if menu == "Dashboard":

        st.title("📊 Dashboard Overview")

        students = load_sheet("Students", ["Name", "Roll", "Course", "Semester"])
        results = load_sheet("Results", ["Roll", "Subject", "Marks"])

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Students", len(students))
        col2.metric("Total Results", len(results))
        col3.metric("System Status", "Active")

        if not results.empty:
            st.subheader("📈 Performance Chart")
            fig = px.bar(results, x="Subject", y="Marks", color="Subject")
            st.plotly_chart(fig, use_container_width=True)

    # ---------------- STUDENT MODULE ----------------
    elif menu == "Student Management":

        st.title("👨‍🎓 Student Management")

        name = st.text_input("Student Name")
        roll = st.text_input("Roll Number")
        course = st.selectbox("Course", ["BCA", "MCA", "BBA", "MBA"])
        semester = st.number_input("Semester", 1, 8)

        if st.button("Add Student"):

            df = pd.DataFrame([[name, roll, course, semester]],
                              columns=["Name", "Roll", "Course", "Semester"])

            save_sheet("Students", df)
            st.success("Student Added Successfully")

        st.subheader("📋 Student List")
        st.dataframe(load_sheet("Students", ["Name", "Roll", "Course", "Semester"]))

    # ---------------- RESULTS MODULE ----------------
    elif menu == "Results Management":

        st.title("📊 Results Entry")

        roll = st.text_input("Roll Number")
        subject = st.text_input("Subject")
        marks = st.number_input("Marks", 0, 100)

        if st.button("Save Result"):

            df = pd.DataFrame([[roll, subject, marks]],
                              columns=["Roll", "Subject", "Marks"])

            save_sheet("Results", df)
            st.success("Result Saved")

        st.subheader("📋 Results Data")
        st.dataframe(load_sheet("Results", ["Roll", "Subject", "Marks"]))

    # ---------------- ATTENDANCE ----------------
    elif menu == "Attendance":

        st.title("📅 Attendance System")

        roll = st.text_input("Roll Number")
        attended = st.number_input("Classes Attended", 0)
        total = st.number_input("Total Classes", 0)

        if st.button("Update Attendance"):

            percent = round((attended / total) * 100, 2) if total > 0 else 0

            df = load_sheet("Attendance", ["Roll", "Attended", "Total", "Percentage"])

            df = df[df["Roll"] != roll]
            df.loc[len(df)] = [roll, attended, total, percent]

            save_sheet("Attendance", df)

            st.success(f"Attendance Updated: {percent}%")

    # ---------------- ANALYTICS ----------------
    elif menu == "Analytics":

        st.title("📈 Analytics Dashboard")

        df = load_sheet("Results", ["Roll", "Subject", "Marks"])

        if not df.empty:

            st.plotly_chart(px.box(df, x="Subject", y="Marks"), use_container_width=True)
            st.plotly_chart(px.pie(df, names="Subject"), use_container_width=True)

        else:
            st.warning("No Data Available")

    # ---------------- CERTIFICATE ----------------
    elif menu == "Certificate Generator":

        st.title("🏆 Certificate Generator")

        name = st.text_input("Student Name")
        roll = st.text_input("Roll Number")
        course = st.text_input("Course")

        if st.button("Generate Certificate"):

            file = generate_certificate(name, roll, course)

            with open(file, "rb") as f:
                st.download_button("Download Certificate", f, file_name=file)

    # ---------------- BACKUP ----------------
    elif menu == "Backup System":

        st.title("💾 System Backup")

        if st.button("Create Backup"):

            backup_excel()
            st.success("Backup Created Successfully")

    # ---------------- LOGOUT ----------------
    elif menu == "Logout":

        st.session_state.login = False
        st.success("Logged Out Successfully")
        st.rerun()
