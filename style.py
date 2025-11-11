import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------- PAGE SETUP --------------------
st.set_page_config(page_title="SkillBot Career & Personality Profiler", layout="centered")

# -------------------- CUSTOM LIGHT THEME (FULL PAGE BACKGROUND) --------------------
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"], .stApp {
        height: 100%;
        width: 100%;
        margin: 0;
        padding: 0;
        background-color: #f5f9ff; /* 👈 Light full-page background */
        background-size: cover;
        background-attachment: fixed;
        font-family: 'Poppins', sans-serif;
    }

    .stApp {
        max-width: 900px;
        margin: 40px auto;
        background-color: #ffffff;
        padding: 30px 40px;
        border-radius: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
    }

    h1, h2, h3 {
        color: #004c91;
        text-align: center;
    }

    p, label, div, span {
        color: #333333;
    }

    .stButton > button {
        background-color: #1e88e5;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #1565c0;
        transform: scale(1.03);
    }

    .question-box {
        background-color: #f0f6ff;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        margin-top: 20px;
        box-shadow: 0px 3px 8px rgba(0,0,0,0.05);
    }

    .css-1d391kg, .block-container {
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- LOAD DATA --------------------
try:
    questions = pd.read_csv("questions.csv")
    careers = pd.read_csv("careers.csv")
    tci_questions = pd.read_csv("tci_questions.csv")
except FileNotFoundError as e:
    st.error(f"Error loading data file: {e}. Make sure 'questions.csv', 'careers.csv', and 'tci_questions.csv' are in the correct directory.")
    st.stop()

# -------------------- SESSION STATE --------------------
defaults = {
    "page": "intro", # Controls RIASEC internal page flow
    "index": 0,      # Controls RIASEC question index
    "answers": [],   # Stores RIASEC answers
    "tci_page": "intro", # Controls TCI internal page flow
    "tci_index": 0,      # Controls TCI question index
    "tci_answers": [],   # Stores TCI answers
    "riasec_scores": None,
    "tci_scores": None,
    "sidebar_choice": "Home", # Controls sidebar selection
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

def restart_all():
    for key, val in defaults.items():
        st.session_state[key] = val

# -------------------- TEST FLOW FUNCTIONS --------------------
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

# -------------------- SIDEBAR --------------------
st.sidebar.title("🧭 Navigation")
sidebar_options = ["Home", "RIASEC Test", "TCI Test", "Dashboard"]
selected_index = sidebar_options.index(st.session_state.sidebar_choice)
st.session_state.sidebar_choice = st.sidebar.radio(
    "Choose a section:",
    sidebar_options,
    index=selected_index
)
choice = st.session_state.sidebar_choice

# =====================================================
# HOME PAGE
# =====================================================
if choice == "Home":
    st.title("🎓 SkillBot Career & Personality Profiler")
    st.write("""
        Discover your ideal **career path** and **personality traits** using two scientific models:
        - 🧭 **RIASEC (Holland Codes)** — measures your work interests  
        - 🧠 **TCI (Temperament & Character Inventory)** — measures your personality

        Take both tests to unlock your personalized dashboard!
    """)
    st.image("https://upload.wikimedia.org/wikipedia/commons/3/3c/Holland_RIASEC_model.png", use_container_width=True)

    if st.button("Start Now ➡️"):
        st.session_state.page = "quiz"
        st.session_state.index = 0
        st.session_state.answers = []
        st.session_state.sidebar_choice = "RIASEC Test"
        st.rerun()

# =====================================================
# RIASEC TEST
# =====================================================
elif choice == "RIASEC Test":
    if st.session_state.page == "intro":
        st.title("🧭 RIASEC Interest Profiler")
        st.write("Rate how much you’d enjoy different work activities. Your answers reveal your work interest pattern.")
        if st.button("Start RIASEC Test"):
            st.session_state.page = "quiz"
            st.session_state.index = 0
            st.session_state.answers = []
            st.rerun()

    elif st.session_state.page == "quiz":
        if st.session_state.index < len(questions):
            q_idx = st.session_state.index
            q = questions.iloc[q_idx]
            st.markdown(f"<div class='question-box'><h3>Question {q_idx + 1} of {len(questions)}</h3><p>{q['question']}</p></div>", unsafe_allow_html=True)
            options = {
                "Strongly Disagree": "😠",
                "Disagree": "🙁",
                "Neutral": "😐",
                "Agree": "🙂",
                "Strongly Agree": "🤩"
            }
            cols = st.columns(len(options))
            for i, (label, icon) in enumerate(options.items()):
                if cols[i].button(f"{icon} {label}", key=f"riasec_q{q_idx}_option{i}"):
                    next_question(label)
        else:
            st.session_state.page = "riasec_results"
            st.rerun()

    elif st.session_state.page == "riasec_results":
        st.title("🎯 Your RIASEC Profile")
        if not st.session_state.answers:
            st.warning("Please complete the RIASEC test first.")
        else:
            df = questions.copy()
            df["answer"] = st.session_state.answers
            rating_map = {"Strongly Disagree": 1, "Disagree": 2, "Neutral": 3, "Agree": 4, "Strongly Agree": 5}
            df["score"] = df["answer"].map(rating_map)
            riasec_scores = df.groupby("category")["score"].mean().sort_values(ascending=False)
            st.session_state.riasec_scores = riasec_scores

            st.bar_chart(riasec_scores)
            top = riasec_scores.head(3).index.tolist()
            st.success(f"Your top RIASEC types are: **{', '.join(top)}**")

            if st.button("Next ➡️ Go to TCI Test"):
                st.session_state.tci_page = "intro"
                st.session_state.tci_index = 0
                st.session_state.tci_answers = []
                st.session_state.sidebar_choice = "TCI Test"
                st.rerun()
            if st.button("🔁 Restart RIASEC Test"):
                st.session_state.page = "intro"
                st.session_state.index = 0
                st.session_state.answers = []
                st.rerun()

# =====================================================
# TCI TEST
# =====================================================
elif choice == "TCI Test":
    if st.session_state.tci_page == "intro":
        st.title("🧠 Temperament & Character Inventory (TCI)")
        st.write("""
            The TCI measures seven personality traits:  
            Novelty Seeking, Harm Avoidance, Reward Dependence,  
            Persistence, Self-Directedness, Cooperativeness, and Self-Transcendence.
        """)
        if st.button("Start TCI Test"):
            st.session_state.tci_page = "quiz"
            st.session_state.tci_index = 0
            st.session_state.tci_answers = []
            st.rerun()

    elif st.session_state.tci_page == "quiz":
        if st.session_state.tci_index < len(tci_questions):
            q_idx = st.session_state.tci_index
            q = tci_questions.iloc[q_idx]
            st.markdown(f"<div class='question-box'><h3>Question {q_idx + 1} of {len(tci_questions)}</h3><p>{q['question']}</p></div>", unsafe_allow_html=True)
            cols = st.columns(2)
            if cols[0].button("✅ True", key=f"tci_q{q_idx}_true"):
                next_tci("T")
            if cols[1].button("❌ False", key=f"tci_q{q_idx}_false"):
                next_tci("F")
        else:
            st.session_state.tci_page = "tci_results"
            st.rerun()

    elif st.session_state.tci_page == "tci_results":
        st.title("🧩 Your TCI Personality Profile")

        if not st.session_state.tci_answers:
            st.warning("Please complete the TCI test first.")
        else:
            df = tci_questions.copy()
            df["answer"] = st.session_state.tci_answers
            df["score"] = df["answer"].map({"T": 1, "F": 0})
            tci_scores = df.groupby("trait")["score"].sum()
            st.session_state.tci_scores = tci_scores

            fig = px.bar(
                tci_scores,
                x=tci_scores.index,
                y=tci_scores.values,
                labels={"x": "Trait", "y": "Score"},
                title="Temperament and Character Dimensions",
                color=tci_scores.index
            )
            st.plotly_chart(fig, use_container_width=True)
            st.info("High scores indicate a stronger presence of that trait.")

            if st.button("View Combined Dashboard ➡️"):
                st.session_state.sidebar_choice = "Dashboard"
                st.rerun()
            if st.button("🔁 Restart TCI Test"):
                st.session_state.tci_page = "intro"
                st.session_state.tci_index = 0
                st.session_state.tci_answers = []
                st.rerun()

# =====================================================
# DASHBOARD (COMBINED RESULTS)
# =====================================================
elif choice == "Dashboard":
    st.title("📊 Combined Career & Personality Dashboard")

    riasec_scores = st.session_state.get("riasec_scores", None)
    tci_scores = st.session_state.get("tci_scores", None)

    if riasec_scores is None or tci_scores is None:
        st.warning("⚠️ Please complete both tests first (RIASEC and TCI).")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("RIASEC Interests")
            fig1 = px.bar(
                riasec_scores,
                x=riasec_scores.index,
                y=riasec_scores.values,
                title="Work Interest Types (RIASEC)",
                color=riasec_scores.index
            )
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            st.subheader("TCI Personality Traits")
            fig2 = px.bar(
                tci_scores,
                x=tci_scores.index,
                y=tci_scores.values,
                labels={"x": "Trait", "y": "Score"},
                title="Personality Traits (TCI)",
                color=tci_scores.index
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.divider()
        st.subheader("🧠 Insight Summary")

        top_interest = riasec_scores.idxmax()
        top_trait = tci_scores.idxmax()
        st.write(f"Your strongest **career interest** is **{top_interest}**, and your dominant **personality trait** is **{top_trait}**.")

        if top_interest == "Social" and top_trait in ["Cooperativeness", "Reward Dependence"]:
            st.success("✅ You might excel in people-centered fields such as teaching, healthcare, or counseling.")
        elif top_interest == "Investigative" and top_trait in ["Persistence", "Self-Directedness"]:
            st.success("✅ You may thrive in analytical or research careers, like data science or engineering.")
        elif top_interest == "Artistic" and top_trait in ["Novelty Seeking", "Self-Transcendence"]:
            st.success("✅ Creative roles such as design, writing, or media could fit your personality.")
        else:
            st.info("Use both profiles to guide your exploration — your mix of traits is unique!")

        if st.button("🏠 Back to Home"):
            restart_all()
            st.session_state.sidebar_choice = "Home"
            st.rerun()



