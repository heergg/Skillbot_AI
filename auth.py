import streamlit as st
import pandas as pd
import os

USER_FILE = "users.csv"

# create user file if it doesn't exist
if not os.path.exists(USER_FILE):
    pd.DataFrame(columns=["email", "password"]).to_csv(USER_FILE, index=False)

def signup(email, password):
    users = pd.read_csv(USER_FILE)
    if email in users["email"].values:
        return False
    pd.DataFrame({"email": [email], "password": [password]}).to_csv(USER_FILE, mode="a", header=False, index=False)
    return True

def login(email, password):
    users = pd.read_csv(USER_FILE)
    if email in users["email"].values:
        stored_pw = users.loc[users["email"] == email, "password"].values[0]
        if stored_pw == password:
            st.session_state["logged_in"] = True
            st.session_state["email"] = email
            return True
    return False
