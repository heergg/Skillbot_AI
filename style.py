import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import auth
import os

# -------------------- PAGE SETUP --------------------
st.set_page_config(page_title="SkillBot Interest Profiler", layout="centered")

# -------------------- CUSTOM CSS --------------------
st.markdown("""
    <style>
    /* ----------- GLOBAL STYLES ----------- */
    body {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #f8fbff, #fdfcfb);
        color: #333333;
    }
    .stApp {
        max-width: 800px;
        margin: auto;
        background-color: #ffffff;
        padding: 40px 30px;
        border-radius: 16px;
        box-shadow: 0px 6px 16px rgba(0, 0, 0, 0.08);
    }

    h1, h2, h3 {
        color: #007acc;
        text-align: center;
        font-weight: 600;
    }
    h1 {
        font-size: 2rem;
        margin-bottom: 10px;
    }

    /* ----------- BUTTON STYLES ----------- */
    .stButton > button {
        background: linear-gradient(to right, #81d4fa, #4fc3f7);
        color: #ffffff !important;
        border: none;
        padding: 12px 20px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 12px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
    }
    .stButton > button:hover {
        background: linear-gradient(to right, #4fc3f7, #29b6f6);
        transform: scale(1.04);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* ----------- QUESTION CARD ----------- */
    .question-box {
        background: #f9fbfd;
        padding: 25px 20px;
        border-radius: 14px;
        text-align: center;
        margin: 25px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e3f2fd;
    }
    .question-box h3 {
        color: #0288d1;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .question-box p {
        font-size: 1.1rem;
        color: #444;
        margin-bottom: 0;
    }

    /* ----------- EMOJI BUTTONS ----------- */
    .emoji-btn {
        display: inline-block;
        background: #e3f2fd;
        color: #0277bd;
        font-size: 18px;
        font-weight: 600;
        border-radius: 10px;
        padding: 12px 18px;
        margin: 8px;
        transition: all 0.3s ease;
        cursor: pointer;
        text-align: center;
        width: 150px;
        border: 1px solid #bbdefb;
    }
    .emoji-btn:hover {
        background: #bbdefb;
        transform: translateY(-3px);
    }

    /* ----------- CHART SECTION ----------- */
    .css-1kyxreq {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
    }

    /* ----------- INFO / TEXT BOXES ----------- */
    .stAlert {
        border-radius: 10px;
        font-size: 0.95rem;
    }

    /* ----------- RESPONSIVE DESIGN ----------- */
    @media screen and (max-width: 768px) {
        .stApp {
            padding: 25px 20px;
        }
        .emoji-btn {
            width: 100%;
            margin: 6px 0;
            font-size: 16px;
        }
        h1 {
            font-size: 1.6rem;
        }
        .question-box p {
            font-size: 1rem;
        }
    }
    </style>
""", unsafe_allow_html=True)


# -------------------- RESPONSES FILE SETUP --------------------
RESPONSES_FILE = "responses/responses.xlsx"
os.makedirs("responses", exist_ok=True)

# -------------------- SESSION --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "home"
if "index" not in st.session_state:
    st.session_state.index = 0
if "answers" not in st.session_state:
    st.session_state.answers = []

# -------------------- NAVBAR --------------------
col1, col2 = st.columns([0.8,0.2])
with col1:
    st.title("🔹 SkillBot Interest Profiler")
with col2:
    if not st.session_state.logged_in:
        if st.button("Register"):
            st.session_state.show_register = True
            st.session_state.show_login = False
        if st.button("Sign In"):
            st.session_state.show_login = True
            st.session_state.show_register = False
    else:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.answers = []
            st.session_state.index = 0
            st.session_state.page = "home"
            st.stop()

# -------------------- REGISTER / LOGIN --------------------
if st.session_state.get("show_register", False):
    st.subheader("Register Now")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")
    if st.button("Register Account"):
        if password != confirm:
            st.error("Passwords do not match")
        elif auth.signup(email, password):
            st.success("Registration successful! Please Sign In now")
            st.session_state.show_register = False
            st.session_state.show_login = True
            st.stop()
        else:
            st.error("Email already exists!")

elif st.session_state.get("show_login", False):
    st.subheader("Sign In")

    if "login_email" not in st.session_state:
        st.session_state.login_email = ""
    if "login_password" not in st.session_state:
        st.session_state.login_password = ""

    st.session_state.login_email = st.text_input("Email", value=st.session_state.login_email)
    st.session_state.login_password = st.text_input("Password", type="password", value=st.session_state.login_password)

    if st.button("Login"):
        if auth.login(st.session_state.login_email, st.session_state.login_password):
            st.session_state.logged_in = True
            st.session_state.show_login = False
            st.session_state.page = "intro"
            st.session_state.username = st.session_state.login_email
            st.stop()
        else:
            st.error("Invalid credentials")

# -------------------- LOAD DATA --------------------
questions = pd.read_csv("questions.csv")
careers = pd.read_csv("careers.csv")

# -------------------- FUNCTIONS --------------------
def restart():
    st.session_state.page = "intro"
    st.session_state.index = 0
    st.session_state.answers = []

def next_question(selected):
    st.session_state.answers.append(selected)
    st.session_state.index += 1
    if st.session_state.index >= len(questions):
        st.session_state.page = "results"
    st.rerun()

def save_responses():
    df = questions.copy()
    df["answer"] = st.session_state.answers
    df["username"] = st.session_state.get("username")
    df["email"] = st.session_state.get("email")

    if os.path.exists(RESPONSES_FILE):
        existing = pd.read_excel(RESPONSES_FILE)
        df_to_save = pd.concat([existing, df], ignore_index=True)
    else:
        df_to_save = df

    df_to_save.to_excel(RESPONSES_FILE, index=False)
    st.success("Your responses have been saved successfully!")

# -------------------- INTRO PAGE --------------------
if st.session_state.page == "intro":
    st.title("Welcome to SkillBot Interest Profiler 🌟")
    st.write("""
    Discover your work interests and explore matching careers.
    Answer **30 fun questions** — it takes just 5 minutes!
    """)
    if st.button("🚀 Start the Profiler"):
        st.session_state.page = "quiz"
        st.experimental_rerun()

# -------------------- QUIZ PAGE --------------------
elif st.session_state.page == "quiz":
    q_idx = st.session_state.index
    q = questions.iloc[q_idx]

    st.markdown(f"<div class='question-box'><h3>Question {q_idx + 1} of {len(questions)}</h3><p>{q['question']}</p></div>", unsafe_allow_html=True)

    options = {
        "Strongly Dislike": "😠",
        "Dislike": "🙁",
        "Unsure": "😐",
        "Like": "🙂",
        "Strongly Like": "🤩"
    }

    # Display as styled emoji buttons
    for label, icon in options.items():
        if st.button(f"{icon} {label}", key=f"{q_idx}-{label}"):
            next_question(label)

# -------------------- RESULTS PAGE --------------------
elif st.session_state.page == "results":
    st.title("🎯 Your Interest Profile")
    df = questions.copy()
    df["answer"] = st.session_state.answers
    rating_map = {"Strongly Dislike": 1, "Dislike": 2, "Unsure": 3, "Like": 4, "Strongly Like": 5}
    df["score"] = df["answer"].map(rating_map)
    riasec_scores = df.groupby("category")["score"].mean().sort_values(ascending=False)
    top = riasec_scores.head(3).index.tolist()
    save_responses()

    st.write("### Your RIASEC Scores")
    fig, ax = plt.subplots()
    ax.bar(riasec_scores.index, riasec_scores.values, color="#4fc3f7")
    ax.set_ylabel("Average Score")
    ax.set_title("RIASEC Interest Profile")
    st.pyplot(fig)

    st.markdown(f"**Your top interests:** 🎨 {', '.join(top)}")
    if st.button("💼 Explore Careers"):
        st.session_state.page = "careers"
        st.session_state.top_interests = top
        st.experimental_rerun()
    if st.button("🔁 Restart"):
        restart()
        st.experimental_rerun()

# -------------------- CAREER PAGE --------------------
elif st.session_state.page == "careers":
    st.title("💼 Career Suggestions")
    top_interests = st.session_state.get("top_interests", [])
    if not top_interests:
        st.warning("Please complete the test first.")
    else:
        for cat in top_interests:
            row = careers[careers["category"] == cat]
            if not row.empty:
                st.markdown(f"### {cat} — {row.iloc[0]['careers']}")
    if st.button("🏠 Back to Start"):
        restart()
        st.experimental_rerun()
