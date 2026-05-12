import streamlit as st
import pandas as pd
import json
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Financial Dashboard", layout="wide")

# ---------------- STYLING ----------------
st.markdown("""
<style>

/* -------- SIDEBAR -------- */
section[data-testid="stSidebar"]{
    background: linear-gradient(180deg, #1E3A8A, #2563EB);
}

/* Sidebar text */
section[data-testid="stSidebar"] *{
    color: white;
}

/* Input box */
section[data-testid="stSidebar"] .stTextInput input {
    background-color: #1E40AF !important;
    color: white !important;
    border: 1px solid #60A5FA !important;
    border-radius: 8px !important;
}

/* Placeholder */
section[data-testid="stSidebar"] input::placeholder {
    color: #cbd5f5 !important;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] button {
    background: rgba(255,255,255,0.15) !important;
    color: white !important;
    border-radius: 8px !important;
}

/* Apply button */
button[kind="primary"] {
    background: linear-gradient(90deg, #10B981, #059669) !important;
    color: white !important;
    border-radius: 10px !important;
    font-weight: bold !important;
}

button[kind="primary"]:hover {
    background: linear-gradient(90deg, #059669, #047857) !important;
}

</style>
""", unsafe_allow_html=True)

USERS_FILE = "users.json"
CATEGORIES_FILE = "categories.json"

# ---------------- USERS ----------------
if "users_loaded" not in st.session_state:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            st.session_state.users = json.load(f)
    else:
        st.session_state.users = {"admin": "1234"}
    st.session_state.users_loaded = True

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = ""

# ---------------- CATEGORIES ----------------
if "categories_loaded" not in st.session_state:
    if os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, "r") as f:
            st.session_state.categories = json.load(f)
    else:
        st.session_state.categories = {"Uncategorized": []}
    st.session_state.categories_loaded = True


def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(st.session_state.users, f)


def save_categories():
    with open(CATEGORIES_FILE, "w") as f:
        json.dump(st.session_state.categories, f)


def add_keyword(category, keyword):
    keyword = keyword.lower().strip()
    if keyword not in st.session_state.categories[category]:
        st.session_state.categories[category].append(keyword)
        save_categories()


# ---------------- LOGIN ----------------
if not st.session_state.logged_in:

    st.title(" 💰 Financial Dashboard")

    tab1, tab2 = st.tabs([" 🔐 Login", "Register"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if u in st.session_state.users and st.session_state.users[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        nu = st.text_input("Create Username")
        np = st.text_input("Create Password", type="password")

        if st.button("Register"):
            if nu in st.session_state.users:
                st.error("User exists")
            else:
                st.session_state.users[nu] = np
                save_users()
                st.success("Registered! Login now.")

    st.stop()


# ---------------- CATEGORIZATION ----------------
def categorize(df):
    df["Category"] = "Uncategorized"

    for cat, keywords in st.session_state.categories.items():
        if cat == "Uncategorized":
            continue

        for i, row in df.iterrows():
            details = str(row["Details"]).lower()

            if any(k in details for k in keywords):
                df.at[i, "Category"] = cat

    return df


# ---------------- LOAD DATA ----------------
def load_data(file):
    try:
        if file is None:
            st.warning("Please upload a file")
            return None

        # RESET POINTER (VERY IMPORTANT)
        file.seek(0)

        # Read CSV safely
        df = pd.read_csv(file)

        # Check empty dataframe
        if df.empty:
            st.error("Uploaded file is empty!")
            return None

        # Clean columns
        df.columns = df.columns.str.strip()

        # Required columns check
        required_cols = ["Date", "Details", "Amount", "Debit/Credit"]
        for col in required_cols:
            if col not in df.columns:
                st.error(f"Missing column: {col}")
                return None

        # Clean data
        df["Amount"] = (
            df["Amount"]
            .astype(str)
            .str.replace(",", "")
            .astype(float)
        )

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        return categorize(df)

    except pd.errors.EmptyDataError:
        st.error("File is empty or invalid CSV format ")
        return None

    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None


# ---------------- MAIN ----------------
def main():

    st.title(" 💰 Financial Dashboard")

    uploaded = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded:
        st.session_state.file = uploaded

    if "file" not in st.session_state:
        st.info("Upload CSV to start")
        return

    df = load_data(st.session_state.file)

    debits = df[df["Debit/Credit"] == "Debit"].copy()
    credits = df[df["Debit/Credit"] == "Credit"].copy()

    # ---------------- SIDEBAR ----------------
    st.sidebar.title("Navigation")
    st.sidebar.success("File uploaded!")

    # User Info
    st.sidebar.markdown(f"👤 **User:** {st.session_state.current_user}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Quick stats
    st.sidebar.markdown("### Quick Stats")
    st.sidebar.write(f" Expenses: {debits['Amount'].sum():,.0f}")
    st.sidebar.write(f" Income: {credits['Amount'].sum():,.0f}")

    # Category search
    search = st.sidebar.text_input("🔍 Search Category")

    st.sidebar.subheader(" 📂 Categories")

    for c in st.session_state.categories:
        if search.lower() in c.lower():
            st.sidebar.write("•", c)

    new_cat = st.sidebar.text_input("Add Category")

    if st.sidebar.button("Add Category"):
        if new_cat and new_cat not in st.session_state.categories:
            st.session_state.categories[new_cat] = []
            save_categories()
            st.sidebar.success("Added")
            st.rerun()

    # ---------------- METRICS ----------------
    c1, c2, c3 = st.columns(3)

    c1.metric(" 💸 Expenses", f"AED {debits['Amount'].sum():,.2f}")
    c2.metric(" 💵 Income", f"AED {credits['Amount'].sum():,.2f}")
    c3.metric(" 🏦 Balance", f"AED {(credits['Amount'].sum()-debits['Amount'].sum()):,.2f}")

    tab1, tab2 = st.tabs(["Expenses", "Credits"])

    # -------- EXPENSES --------
    with tab1:

        st.subheader("Edit Categories")

        edited_df = st.data_editor(
            debits[["Date", "Details", "Amount", "Category"]],
            use_container_width=True,
            key="editor"
        )

        if st.button("Apply Changes", type="primary"):
            for i, row in edited_df.iterrows():
                new_cat = row["Category"]
                details = row["Details"]

                debits.at[i, "Category"] = new_cat
                add_keyword(new_cat, details)

            st.success("Changes Applied!")
            st.rerun()

        summary = debits.groupby("Category")["Amount"].sum().reset_index()

        st.subheader("Expense Summary")
        st.dataframe(summary)

        if not summary.empty:

            fig, ax = plt.subplots(1, 2, figsize=(12, 5))

            ax[0].pie(summary["Amount"], labels=summary["Category"], autopct="%1.1f%%")
            ax[0].set_title("Spending Distribution")

            ax[1].bar(summary["Category"], summary["Amount"])
            ax[1].set_title("Category Spending")

            plt.xticks(rotation=45)
            st.pyplot(fig)

    # -------- CREDITS --------
    with tab2:
        edited_df1 = st.data_editor(
            credits[["Date", "Details", "Amount", "Category"]],
            use_container_width=True,
            key="editor1"
        )

        if st.button("Apply Changes", type="primary",key="button1"):

            for i, row in edited_df1.iterrows():
                new_cat = row["Category"]
                details = row["Details"]

                credits.at[i, "Category"] = new_cat
                add_keyword(new_cat, details)

            st.success("Changes Applied!")
            st.rerun()

        summary = credits.groupby("Category")["Amount"].sum().reset_index()

        st.subheader("Credits Summary")
        st.dataframe(credits)

        if not summary.empty:

            fig, ax = plt.subplots(1, 2, figsize=(12, 5))

            ax[0].pie(summary["Amount"], labels=summary["Category"], autopct="%1.1f%%")
            ax[0].set_title("Spending Distribution")

            ax[1].bar(summary["Category"], summary["Amount"])
            ax[1].set_title("Category Spending")

            plt.xticks(rotation=45)
            st.pyplot(fig)





# RUN
main()