import pandas as pd
import os
from security import encrypt_password

USER_FILE = "data_users.xlsx"

# ---------------- INIT FILE ----------------
def init_users():
    if not os.path.exists(USER_FILE):
        df = pd.DataFrame(columns=["username", "password", "role"])
        df.to_excel(USER_FILE, index=False)

# ---------------- REGISTER USER ----------------
def register_user(username, password, role="user"):
    init_users()
    df = pd.read_excel(USER_FILE)

    # check duplicate user
    if username in df["username"].values:
        return False

    hashed = encrypt_password(password)

    new_user = pd.DataFrame([[username, hashed, role]],
                            columns=["username", "password", "role"])

    df = pd.concat([df, new_user], ignore_index=True)
    df.to_excel(USER_FILE, index=False)

    return True

# ---------------- LOGIN USER ----------------
def login_user(username, password):
    init_users()
    df = pd.read_excel(USER_FILE)

    hashed = encrypt_password(password)

    user = df[(df["username"] == username) & (df["password"] == hashed)]

    if not user.empty:
        return user.iloc[0]["role"]

    return None