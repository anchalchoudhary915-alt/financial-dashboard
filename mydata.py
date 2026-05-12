import os
import json
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
st.set_page_config(page_title="Simple Finance App",layout="wide")
if "categories" not in st.session_state:
    st.session_state.categories={
        "Uncategorized":[]
    }
if os.path.exists("categories.json"):
    with open("categories.json","r") as fp:
        st.session_state.categories=json.load(fp)
def categorize_transactions(df):
    df["Category"]="Uncategorized"
    for category,keywords in st.session_state.categories.items():
        if category=="Uncategorized" or not keywords:
            continue
        lowered_keywords=[keyword.lower().strip() for keyword in keywords]
        for idx,row in df.iterrows():
            details=row["Details"].lower().strip()
            if details in lowered_keywords:
                df.at[idx,"Category"]=category
    return df

def add_keyword_to_category(new_category, keyword):
    keyword=keyword.strip()
    if keyword and keyword not in st.session_state.categories[new_category]:
        st.session_state.categories[new_category].append(keyword)
        savecat()
        return True
    return False

def load_transactions(fn):
    try:
        df=pd.read_csv(fn)
        df=df.iloc[:,:-1]
        df.columns=[col.strip() for col in df.columns]
        df["Amount"]=df["Amount"].str.replace(",","").astype(float)
        df["Date"]=pd.to_datetime(df["Date"],format="%d %b %Y")
        return categorize_transactions(df)
    except Exception as e:
        st.error(f"Error processing file {str(e)}")
        return None
def savecat():
    with open("categories.json","w") as fp:
        json.dump(st.session_state.categories, fp)

st.title("Simple Finance Dashboard")
uploaded_file=st.file_uploader("Upload your transaction file",type=["csv"])
if uploaded_file is not None:
    df = load_transactions(uploaded_file)
    if df is not None:
        creditsdf=df[df["Debit/Credit"]=="Credit"]
        deditsdf = df[df["Debit/Credit"] == "Debit"]
        st.session_state.debitsdf=deditsdf
        tab1,tab2=st.tabs(["Expenses (Debits)","Payments (Credits)"])
        with tab1:
            st.subheader("Categories")
            catnam=st.text_input("Category Name",key="a")
            btnadd=st.button("Add New Category",key="b1")
            if catnam and btnadd:
                if catnam not in st.session_state.categories:
                    st.session_state.categories[catnam]=[]
                    savecat()
                    st.success("New Category Added")
                    st.rerun()
            st.subheader("Your Expenses")
            edited_df=st.data_editor(st.session_state.debitsdf[["Date","Details","Amount","Category"]],
                           column_config={
                               "Date":st.column_config.DateColumn("Date",format="DD/MM/YYYY"),
                               "Amount":st.column_config.NumberColumn("Amount",format="%.2f USD"),
                               "Category":st.column_config.SelectboxColumn(options=
    list(st.session_state.categories.keys()))
                           },hide_index=True,width='stretch',key="dedit")
            save_button = st.button("Apply Changes", type="primary")
            if save_button:
                for idx,row in edited_df.iterrows():
                    new_category=row["Category"]
                    if new_category==st.session_state.debitsdf.at[idx,"Category"]:
                        continue
                    details=row["Details"]
                    st.session_state.debits_df.at[idx, "Category"] = new_category
                    add_keyword_to_category(new_category, details)
        with tab2:
            st.subheader("Credits")

