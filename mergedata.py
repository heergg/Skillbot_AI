import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# -------------------- SUPABASE SETUP --------------------
SUPABASE_URL = "https://jaztokuyzxettemexcrc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImphenRva3V5enhldHRlbWV4Y3JjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI5NTU4OTMsImV4cCI6MjA3ODUzMTg5M30.I7Q-fAKRqYFzsJoyt7jQD1Vm1eB0sQKo17-ikA5VFBY"  # Replace with your key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------- PAGE SETUP --------------------
st.set_page_config(page_title="SkillBot Career & Personality Profiler", layout="centered")

# -------------------- LOAD DATA --------------------
try:
    questions = pd.read_csv("questions.csv")
    careers = pd.read_csv("careers.csv")
    tci_questions = pd.read_csv("tci_questions.csv")
except FileNotFoundError as e:
    st.error(f"Error loading data file: {e}")
    st.stop()

# -------------------- SESSION STATE --------------------
defaults = {
    "page": "intro",
    "index": 0,
    "answers": [],
    "tci_page": "intro",
    "tci_index": 0,
    "tci_answers": [],
    "riasec_scores": None,
    "tci_scores": None,
    "sidebar_choice": "Home",
    "user": None,  # Supabase user object
    "access_token": None
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def restart_all():
    for k, v in defaults.items():
        st.session_state[k] = v

# -------------------- AUTH HELPERS --------------------
def signup_user(email, password):
    return supabase.auth.sign_up({"email": email, "password": password})

def login_user(email, password):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

def logout_user():
    st.session_state.user = None
    st.session_state.access_token = None
    st.session_state.sidebar_choice = "Home"
    st.success("Logged out successfully!")

# -------------------- DB SAVE HELPERS --------------------
def save_results_to_supabase(user_id, riasec, tci):
    try:
        # Convert Pandas Series to normal dict
        riasec_dict = riasec.to_dict()
        tci_dict = tci.to_dict()

        response = supabase.table("test_results").insert({
            "user_id": user_id,

            # ----- RIASEC -----
            "riasec_R": riasec_dict.get("R"),
            "riasec_I": riasec_dict.get("I"),
            "riasec_A": riasec_dict.get("A"),
            "riasec_S": riasec_dict.get("S"),
            "riasec_E": riasec_dict.get("E"),
            "riasec_C": tci_dict.get("C"),

            # ----- TCI -----
            "tci_Persistence": tci_dict.get("Persistence"),
            "tci_HarmAvoidance": tci_dict.get("Harm Avoidance"),
            "tci_Cooperativeness": tci_dict.get("Cooperativeness"),
            "tci_NoveltySeeking": tci_dict.get("Novelty Seeking"),
            "tci_RewardDependence": tci_dict.get("Reward Dependence"),
            "tci_SelfDirectedness": tci_dict.get("Self-Directedness"),
            "tci_SelfTranscendence": tci_dict.get("Self-Transcendence"),
        }).execute()

        st.success("✅ Test results saved into separate columns!")

    except Exception as e:
        st.error(f"⚠️ Could not save results: {e}")


def upload_marksheet(user_id, file):
    try:
        file_bytes = file.read()
        filename = f"{user_id}_{file.name}"

        # Upload file
        supabase.storage.from_("marksheets").upload(filename, file_bytes)

        # Get public URL (returns a string)
        public_url = supabase.storage.from_("marksheets").get_public_url(filename)

        st.success("✅ Marksheet uploaded successfully!")
        return public_url

    except Exception as e:
        st.error(f"Error uploading file: {e}")
        return None


def save_profile(user_id, name, gender, age, qualification, marksheet_url):
    try:
        response = supabase.table("profiles").upsert({
            "user_id": user_id,
            "full_name": name,
            "gender": gender,
            "age": age,
            "qualification": qualification,
            "marksheet_url": marksheet_url
        }).execute()

        if response.data is not None:
            st.success("✅ Profile created successfully!")
        else:
            st.warning("⚠️ Could not save profile. Check your table schema or permissions.")

    except Exception as e:
        st.error(f"Failed to save profile: {e}")

# -------------------- HELPER FUNCTIONS --------------------
def next_question(selected):
    st.session_state.answers.append(selected)
    st.session_state.index += 1
    if st.session_state.index >= len(questions):
        st.session_state.page = "riasec_results"
    st.rerun()

def next_tci(selected):
    st.session_state.tci_answers.append(selected)
    st.session_state.tci_index += 1
    if st.session_state.tci_index >= len(tci_questions):
        st.session_state.tci_page = "tci_results"
    st.rerun()

# =====================================================
# SIDEBAR NAVIGATION
# =====================================================
st.sidebar.title("🧭 Navigation")
options = ["Home", "RIASEC Test", "TCI Test", "Dashboard", "Sign Up / Login", "Profile Creation (Hidden)"]
choice = st.sidebar.radio("Choose a section:", options, index=options.index(st.session_state.sidebar_choice))
st.session_state.sidebar_choice = choice

# =====================================================
# HOME PAGE
# =====================================================
if choice == "Home":
    st.title("🎓 SkillBot Career & Personality Profiler")
    st.write("""
        Discover your ideal **career path** and **personality traits** using:
        - **RIASEC (Holland Codes)**
        - **TCI (Temperament & Character Inventory)**
    """)
    if st.button("Start Now ➡️"):
        st.session_state.page = "quiz"
        st.session_state.sidebar_choice = "RIASEC Test"
        st.rerun()

# =====================================================
# RIASEC TEST
# =====================================================
elif choice == "RIASEC Test":
    if st.session_state.page == "intro":
        st.title("🧭 RIASEC Interest Profiler")
        if st.button("Start RIASEC Test"):
            st.session_state.page = "quiz"
            st.session_state.index = 0
            st.session_state.answers = []
            st.rerun()
    elif st.session_state.page == "quiz":
        q_idx = st.session_state.index
        if q_idx < len(questions):
            q = questions.iloc[q_idx]
            st.markdown(f"### Question {q_idx + 1} of {len(questions)}")
            st.markdown(f"**{q['question']}**")
            options_map = {"Strongly Disagree":"😠","Disagree":"🙁","Neutral":"😐","Agree":"🙂","Strongly Agree":"🤩"}
            cols = st.columns(len(options_map))
            for i, (label, icon) in enumerate(options_map.items()):
                if cols[i].button(f"{icon} {label}", key=f"riasec_q{q_idx}_{i}"):
                    next_question(label)
    elif st.session_state.page == "riasec_results":
        st.title("Your RIASEC Profile")
        df = questions.copy()
        df["answer"] = st.session_state.answers
        rating_map = {"Strongly Disagree":1,"Disagree":2,"Neutral":3,"Agree":4,"Strongly Agree":5}
        df["score"] = df["answer"].map(rating_map)
        riasec_scores = df.groupby("category")["score"].mean().sort_values(ascending=False)
        st.session_state.riasec_scores = riasec_scores
        st.bar_chart(riasec_scores)
        top = riasec_scores.head(3).index.tolist()
        st.success(f"Your top RIASEC types are: **{', '.join(top)}**")
        if st.button("Next ➡️ Go to TCI Test"):
            st.session_state.sidebar_choice = "TCI Test"
            st.rerun()

# =====================================================
# TCI TEST
# =====================================================
elif choice == "TCI Test":
    if st.session_state.tci_page == "intro":
        st.title("🧠 Temperament & Character Inventory (TCI)")
        if st.button("Start TCI Test"):
            st.session_state.tci_page = "quiz"
            st.session_state.tci_index = 0
            st.session_state.tci_answers = []
            st.rerun()
    elif st.session_state.tci_page == "quiz":
        q_idx = st.session_state.tci_index
        if q_idx < len(tci_questions):
            q = tci_questions.iloc[q_idx]
            st.markdown(f"### Question {q_idx + 1} of {len(tci_questions)}")
            st.markdown(f"**{q['question']}**")
            col1, col2 = st.columns(2)
            if col1.button("✅ True", key=f"tci_t{q_idx}"):
                next_tci("T")
            if col2.button("❌ False", key=f"tci_f{q_idx}"):
                next_tci("F")
    elif st.session_state.tci_page == "tci_results":
        st.title("Your TCI Personality Profile")
        df = tci_questions.copy()
        df["answer"] = st.session_state.tci_answers
        df["score"] = df["answer"].map({"T": 1, "F": 0})
        tci_scores = df.groupby("trait")["score"].sum()
        st.session_state.tci_scores = tci_scores
        fig = px.bar(tci_scores, x=tci_scores.index, y=tci_scores.values, labels={"x": "Trait","y": "Score"})
        st.plotly_chart(fig, use_container_width=True)
        if st.button("View Combined Dashboard ➡️"):
            st.session_state.sidebar_choice = "Dashboard"
            st.rerun()

# =====================================================
# DASHBOARD
# =====================================================
elif choice == "Dashboard":
    st.title("📊 Combined Career & Personality Dashboard")
    r, t = st.session_state.riasec_scores, st.session_state.tci_scores
    if r is None or t is None:
        st.warning("Please complete both tests first.")
    else:
        c1, c2 = st.columns(2)
        with c1: st.subheader("RIASEC"); st.bar_chart(r)
        with c2: st.subheader("TCI"); st.bar_chart(t)
        st.divider()
        st.info("Use both profiles to guide your career choices!")
        if st.button("✨ Want more personalized results?"):
            st.session_state.sidebar_choice = "Sign Up / Login"
            st.rerun()

# =====================================================
# SIGN UP / LOGIN
# =====================================================
elif choice == "Sign Up / Login":
    st.title("🔐 Account")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            res = login_user(email, password)
            if res.user:
                st.session_state.user = res.user
                st.session_state.access_token = res.session.access_token
                st.success("✅ Logged in successfully!")
                st.session_state.sidebar_choice = "Profile Creation (Hidden)"
                st.rerun()

    with tab2:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Sign Up"):
            res = signup_user(email, password)
            if res.user:
                st.session_state.user = res.user
                st.session_state.access_token = res.session.access_token
                st.success("✅ Account created successfully!")
                st.session_state.sidebar_choice = "Profile Creation (Hidden)"
                st.rerun()

# =====================================================
# PROFILE CREATION
# =====================================================
elif choice == "Profile Creation (Hidden)":
    st.title("👤 Create Your Profile")
    if st.session_state.user is None:
        st.warning("Please login first.")
    else:
        name = st.text_input("Full Name")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        age = st.number_input("Age", min_value=10, max_value=100)
        qualification = st.selectbox("Qualification", ["Matric","Intermediate","Bachelors","Masters","PhD"])
        marksheet = st.file_uploader("Upload Marksheet", type=["jpg","jpeg","png","pdf"])

        if st.button("Submit Profile"):
            if not all([name, gender, age, qualification, marksheet]):
                st.error("Please fill all fields.")
            else:
                marksheet_url = upload_marksheet(st.session_state.user.id, marksheet)
                if marksheet_url:
                    save_profile(
                        st.session_state.user.id, name, gender, age, qualification, marksheet_url
                    )
                    if st.session_state.riasec_scores is not None and st.session_state.tci_scores is not None:
                        save_results_to_supabase(
                            st.session_state.user.id, st.session_state.riasec_scores, st.session_state.tci_scores
                        )



import cv2
import numpy as np
import pandas as pd
from paddleocr import PaddleOCR
import re

# ------------------------------------------------------------
# 1) Load & preprocess image to fix blur/noise/lighting
# ------------------------------------------------------------
def preprocess_image(path):
    img = cv2.imread(path)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Remove noise
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    # Adaptive threshold (works for colored/noisy marksheets)
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31, 10
    )

    return img, thresh

# ------------------------------------------------------------
# 2) OCR detection using PaddleOCR (much more accurate)
# ------------------------------------------------------------
ocr = PaddleOCR(use_angle_cls=True, lang='en')

def extract_text(img):
    result = ocr.ocr(img)
    text_data = []
    if result and result[0]: # Check if result is not empty and has detections for the first image
        # PaddleOCR can return a list of dictionaries with results per image, or a list of detection tuples.
        # The 'Warning: Unrecognized item format' suggests result[0] is a dictionary.
        if isinstance(result[0], dict) and 'rec_texts' in result[0]:
            # If result[0] is a dictionary and contains 'rec_texts' (a list of text strings)
            text_data = result[0]['rec_texts']
        elif isinstance(result[0], list):
            # Fallback for older PaddleOCR versions or different output formats
            # where result[0] is directly a list of detection items
            for item in result[0]:
                # Handle potential variations in PaddleOCR output format
                if isinstance(item, (list, tuple)) and len(item) == 3: # Format: (bbox, text_str, confidence_float)
                    box_coords, text_str, confidence = item
                    text_data.append(text_str)
                elif isinstance(item, (list, tuple)) and len(item) == 2: # Format: (bbox, (text_str, confidence_float))
                    box_coords, text_info = item
                    if isinstance(text_info, (list, tuple)) and len(text_info) == 2:
                        text_data.append(text_info[0])
                    else:
                        # Fallback if text_info is not a (text, confidence) tuple
                        text_data.append(str(text_info))
                else:
                    print(f"Warning: Unrecognized item format from PaddleOCR: {item}")
        else:
            print(f"Warning: Unrecognized top-level item format from PaddleOCR: {result[0]}")
    return text_data

# ------------------------------------------------------------
# Helper for robust number extraction
# ------------------------------------------------------------
def extract_number_robust(s):
    s = str(s).strip()
    # Find the first sequence of digits, optionally with a decimal point
    match = re.search(r'\d+\.?\d*', s)
    if match:
        try:
            return float(match.group(0)) if '.' in match.group(0) else int(match.group(0))
        except ValueError:
            return None
    return None

# ------------------------------------------------------------
# 3) Convert extracted text into "Subject | Max | Obtained"
# ------------------------------------------------------------
def parse_marks(text_list):
    subjects = []
    maximum = []
    obtained = []

    # Find the starting point of the actual marks table
    start_parsing_from_index = -1
    for idx, text in enumerate(text_list):
        if 'SUBJECT - WISE STATEMENT OF MARKS' in text.upper():
            start_parsing_from_index = idx
            break

    if start_parsing_from_index != -1:
        i = start_parsing_from_index + 1 # Start from the item after the header
    else:
        i = 0 # Fallback to start from beginning if header not found

    # Keywords to ignore when identifying subjects or as noise
    forbidden_subject_keywords = {'SR.NO.', 'SR.NO', 'SUBJECTS', 'MARKS', 'MAXIMUM', 'OBTAINED', 'ANNUAL', 'NO CERTIFICATE'}
    # Single-letter/short strings often misidentified by OCR or irrelevant from the provided raw OCR
    noise_words = {'L', 'E', 'a', 'b', 'c', 'd', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '100', 'FIRST'}

    while i < len(text_list):
        t1_raw = text_list[i].strip()
        t1_upper = t1_raw.upper()

        # Skip empty strings or known noise words/forbidden keywords
        if not t1_raw or t1_upper in forbidden_subject_keywords or t1_raw.lower() in [nw.lower() for nw in noise_words] or len(t1_raw) < 2 and not t1_upper == 'TOTAL':
            i += 1
            continue

        # Check if t1 is a plausible subject
        is_plausible_subject = False
        # A subject should contain at least two alphabetic characters and not be a forbidden/noise word
        if re.search(r'[a-zA-Z]{2,}', t1_raw) and \
           t1_upper not in forbidden_subject_keywords and \
           t1_raw.lower() not in [nw.lower() for nw in noise_words]:
            is_plausible_subject = True

        # Allow specific subjects regardless of strict alpha check or length if they are explicitly known
        specific_subjects_keywords = ["URDU", "ENGLISH", "ISLAMIYAT", "PAKISTAN STUDIES", "MATHEMATICS", "PHYSICS", "CHEMISTRY", "BIOLOGY", "TOTAL"]
        if any(ss in t1_upper for ss in specific_subjects_keywords):
             is_plausible_subject = True

        if is_plausible_subject:
            subject_name = t1_raw

            # Special handling for 'TOTAL' as its numbers are sometimes out of immediate sequence
            if t1_upper == 'TOTAL':
                potential_total_nums = []
                scan_idx = i + 1
                while scan_idx < len(text_list) and len(potential_total_nums) < 3: # Scan up to 3 numbers for safety
                    num = extract_number_robust(text_list[scan_idx])
                    if num is not None:
                        potential_total_nums.append((num, scan_idx)) # Store number and its original index
                    scan_idx += 1

                if len(potential_total_nums) >= 2:
                    # For 'TOTAL', we want the largest two numbers (Total Max and Total Obtained)
                    # Example: 'TOTAL', '49', '850', '426'. We want 850 and 426.
                    # Sort by value to easily pick the max and obtained
                    potential_total_nums.sort(key=lambda x: x[0], reverse=True)

                    subjects.append(subject_name)
                    maximum.append(int(potential_total_nums[0][0])) # Largest number
                    obtained.append(int(potential_total_nums[1][0])) # Second largest number

                    # Advance 'i' past the highest index of the numbers used
                    max_k_used = max(item[1] for item in potential_total_nums[:2])
                    i = max_k_used + 1
                else:
                    i += 1 # Not enough numbers for total, skip
                continue

            # For regular subjects, look for two numbers immediately after the subject name
            found_nums = []
            last_num_idx = i
            scan_idx = i + 1
            num_search_count = 0 # To limit how far we scan for numbers
            while scan_idx < len(text_list) and len(found_nums) < 2 and num_search_count < 4: # Scan up to 4 items ahead
                num = extract_number_robust(text_list[scan_idx])
                if num is not None and num >= 0:
                    # Heuristic to skip potential serial numbers (small number after Max and before another mark)
                    if len(found_nums) == 1 and num < 10 and (scan_idx + 1 < len(text_list)) and extract_number_robust(text_list[scan_idx+1]) is not None:
                        print(f"Skipping potential serial number: {num} for subject {subject_name}") # For debugging
                        # Don't append, just advance scan_idx
                    else:
                        found_nums.append(num)
                    last_num_idx = scan_idx
                scan_idx += 1
                num_search_count += 1

            if len(found_nums) >= 2: # Ensure at least two numbers are found
                subjects.append(subject_name)
                maximum.append(int(found_nums[0]))
                obtained.append(int(found_nums[1]))
                i = last_num_idx + 1 # Advance index past the last number used
            else:
                i += 1 # Not enough numbers for subject marks, advance one position
        else:
            i += 1 # Not a subject candidate, move to next item.

    df = pd.DataFrame({
        "Subject": subjects,
        "Maximum": maximum,
        "Obtained": obtained
    })

    return df

# ------------------------------------------------------------
# 4) MAIN FUNCTION
# ------------------------------------------------------------
def extract_marks_from_marksheet(image_path, output_csv=None):
    img, thresh = preprocess_image(image_path)

    print("🔍 Running OCR...")
    text_list = extract_text(img)

    print("📄 Raw OCR Text:")
    print(text_list)

    df = parse_marks(text_list)

    print("\n📊 Extracted Marks:")
    print(df)

    if output_csv:
        df.to_csv(output_csv, index=False)
        print(f"\n💾 Marks saved to {output_csv}")

    return df


# ------------------------------------------------------------
# 5) Run on your marksheet
# ------------------------------------------------------------
# extract_marks_from_marksheet("/content/IMG_20210617_120733.jpg", output_csv='marksheet_marks.csv')
#Merge both marksheet csv files which are gernerated by OCR

import pandas as pd
# m1 = pd.read_csv('/content/marksheet_marks (5).csv') # This file was not found
# m2 = pd.read_csv('/content/marksheet_marks (7).csv') # This file was not found

# # Assign a unique student ID to each marksheet before merging
# m1['id'] = 1 # Assuming this marksheet is for student_id 1
# m2['id'] = 2 # Assuming this marksheet is for student_id 2

# # Concatenate the dataframes. Now both have an 'id' column.
# merged = pd.concat([m1, m2], axis=0, ignore_index=True)
# merged.to_csv('marksheet_merged.csv', index=False)



#LLM Model


import pandas as pd

# ----------------------------------------------
# SUBFIELDS FOR EACH FIELD
# ----------------------------------------------
SUBFIELDS = {
    "Engineering": [
        "Mechanical Engineering",
        "Electrical Engineering",
        "Civil Engineering",
        "Software Engineering",
        "Chemical Engineering"
    ],
    "Medical": [
        "MBBS",
        "Pharmacy",
        "Physiotherapy",
        "Nursing",
        "Biotechnology"
    ],
    "Computer Science": [
        "Artificial Intelligence",
        "Data Science",
        "Cyber Security",
        "Software Development",
        "IT Management"
    ],
    "Business": [
        "BBA",
        "Marketing",
        "Finance",
        "HR Management",
        "Supply Chain"
    ],
    "Arts": [
        "Psychology",
        "Fine Arts",
        "Mass Communication",
        "English Literature",
        "Sociology"
    ],
    "Commerce": [
        "B.Com",
        "Accounting",
        "Banking",
        "Economics",
        "Business Administration"
    ]
}

# ----------------------------------------------
# LOAD PERSONALITY TEST (RIASEC + TCI)
# ----------------------------------------------
def load_personality(csv_path):
    df = pd.read_csv(csv_path)
    df = df.rename(columns={"user_id": "student_id"})
    return df


# ----------------------------------------------
# LOAD MARKSHEET & CONVERT TO WIDE FORMAT
# ----------------------------------------------
def load_marksheet(csv_path):
    df = pd.read_csv(csv_path)
    df = df.rename(columns={"Obtained": "marks", "Subject": "subject"})
    df = df[["subject", "marks"]]    # Only two columns needed
    df = df[~df["subject"].str.contains("TOTAL", case=False)]  # remove TOTAL rows
    df["subject"] = df["subject"].str.upper().str.strip()
    df = df.groupby("subject")["marks"].max().reset_index()   # handle duplicates
    return df


# ----------------------------------------------
# EXTRACT SUBJECT SCORES (MATH / PHY / ENG etc.)
# ----------------------------------------------
def extract_subject_scores(df):
    subjects = {
        "math": ["MATH", "MATHEMATICS"],
        "physics": ["PHYSICS"],
        "chemistry": ["CHEMISTRY"],
        "biology": ["BIOLOGY"],
        "computer": ["COMPUTER"],
        "english": ["ENGLISH"],
        "urdu": ["URDU"],
        "islamiat": ["ISLAM", "ISLAMIYAT"],
        "pakstudies": ["PAKISTAN"]
    }

    extracted = {}

    for key, keywords in subjects.items():
        extracted[key] = 0  # default
        for kw in keywords:
            row = df[df["subject"].str.contains(kw, case=False)]
            if len(row) > 0:
                extracted[key] = int(row.iloc[0]["marks"])
                break

    return extracted


# ----------------------------------------------
# RULE-BASED SCORING SYSTEM
# ----------------------------------------------
def calculate_best_fit(marks, personality):
    """
    marks: dict, e.g. {"math": 147, "physics":147, "biology":147, "chemistry":138, "english":137, "urdu":131, "computer":130}
    personality: dict, RIASEC + TCI scores scaled 0-5 or 0-100
    Returns: dict of normalized probabilities for each field
    """

    # Initialize raw scores
    scores = {
        "Medical": 0,
        "Engineering": 0,
        "Computer Science": 0,
        "Arts": 0,
        "Business": 0,
        "Commerce": 0
    }

    # -------------------------
    # MARKS WEIGHTS (field relevance)
    # -------------------------
    scores["Medical"] += (marks["biology"]/150)*0.35 + (marks["chemistry"]/150)*0.35 + (marks["physics"]/150)*0.1 + (marks["math"]/150)*0.1 + (marks["english"]/150)*0.05 + (marks["urdu"]/150)*0.05
    scores["Engineering"] += (marks["math"]/150)*0.35 + (marks["physics"]/150)*0.35 + (marks["chemistry"]/150)*0.1 + (marks["biology"]/150)*0.05 + (marks["english"]/150)*0.05 + (marks["urdu"]/150)*0.1
    scores["Computer Science"] += (marks["math"]/150)*0.3 + (marks["physics"]/150)*0.2 + (marks["computer"]/150)*0.25 + (marks["english"]/150)*0.1 + (marks["biology"]/150)*0.05 + (marks["urdu"]/150)*0.1
    scores["Arts"] += (marks["english"]/150)*0.4 + (marks["urdu"]/150)*0.3 + (marks["biology"]/150)*0.05 + (marks["chemistry"]/150)*0.05 + (marks["math"]/150)*0.1 + (marks["physics"]/150)*0.1
    scores["Business"] += (marks["math"]/150)*0.2 + (marks["english"]/150)*0.3 + (marks["urdu"]/150)*0.2 + (marks["biology"]/150)*0.05 + (marks["chemistry"]/150)*0.05 + (marks["physics"]/150)*0.2
    scores["Commerce"] += (marks["math"]/150)*0.3 + (marks["english"]/150)*0.25 + (marks["urdu"]/150)*0.2 + (marks["biology"]/150)*0.05 + (marks["chemistry"]/150)*0.05 + (marks["physics"]/150)*0.15

    # -------------------------
    # PERSONALITY / RIASEC WEIGHTS
    # personality scores assumed 0-5 scale
    # -------------------------
    scores["Medical"] += ((personality.get("riasec_I",0) + personality.get("riasec_A",0))/10) * 0.3
    scores["Engineering"] += ((personality.get("riasec_I",0) + personality.get("riasec_C",0))/10) * 0.3
    scores["Computer Science"] += ((personality.get("riasec_C",0) + personality.get("tci_NoveltySeeking",0))/10) * 0.3
    scores["Arts"] += ((personality.get("riasec_A",0) + personality.get("riasec_E",0))/10) * 0.3
    scores["Business"] += ((personality.get("riasec_E",0) + personality.get("tci_RewardDependence",0))/10) * 0.3
    scores["Commerce"] += ((personality.get("riasec_E",0) + personality.get("riasec_C",0))/10) * 0.3

    # -------------------------
    # NORMALIZE SCORES TO PROBABILITIES
    # -------------------------
    total_score = sum(scores.values())
    probabilities = {field: round(score/total_score, 3) for field, score in scores.items()}

    # Sort by highest probability
    probabilities = dict(sorted(probabilities.items(), key=lambda x: x[1], reverse=True))

    return probabilities



# ----------------------------------------------
# MAIN FUNCTION
# ----------------------------------------------
def recommend_field(personality_csv, marksheet_csv):
    # 1. Load datasets
    p = load_personality(personality_csv)
    m = load_marksheet(marksheet_csv)

    # Single student case
    personality = p.iloc[0].to_dict()

    # Extract subject scores
    marks = extract_subject_scores(m)

    # Score fields
    field_scores = calculate_best_fit(marks, personality)

    # Best field
    best_field = max(field_scores, key=field_scores.get)

    # Subfields
    best_subfields = SUBFIELDS[best_field]

    # Output
    print("Recommended Field:", best_field)
    print("Recommended Subfields:")
    for s in best_subfields:
        print("-", s)

    return best_field, best_subfields

# give there your response file path

    # recommend_field("/content/response.csv", "marksheet_merged.csv") # This line is commented out due to the FileNotFoundError
