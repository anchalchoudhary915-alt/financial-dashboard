import json
import matplotlib.pyplot as plt
from _ast import keyword
import streamlit as st
import pandas as pd
import os


st.set_page_config(page_title="Financial Dashboard",layout="wide")
if "categories" not in st.session_state:
    st.session_state.categories={
        "Uncategorized":[]
    }
if os.path.exists("categories.json"):
    with open("categories.json","r") as fp:
        st.session_state.categories=json.load(fp)

def save_cat():
    with open("categories.json","w") as fp:
        json.dump(st.session_state.categories,fp)

def cat_trans(df):
    df["Category"]="Uncategorized"
    for cat,keywords in st.session_state.categories.items():
        if cat=="Uncategorized" or not keywords:
            continue
        low_key=[keyword.lower().strip() for keyword in keywords]
        for idx,row in df.iterrows():
            det=row["Details"].lower().strip()
            if det in low_key:
                df.at[idx,"Category"]=cat
    return df

def load_trans(fnam):
    try:
        df=pd.read_csv(fnam)
        df=df.iloc[:,:-1]
        df.columns = [col.strip() for col in df.columns]
        df["Amount"]=df["Amount"].str.replace(",","").astype(float)
        df["Date"]=pd.to_datetime(df["Date"],format="%d %b %Y")
        return cat_trans(df)
    except Exception as e:
        st.error(f"Unable to read file {str(e)}")
        return None
def add_keyword_to_cat(new_cat,keyword):
    keyword=keyword.strip()
    if keyword and keyword not in st.session_state.categories[new_cat]:
        st.session_state.categories[new_cat].append(keyword)
        save_cat()
        return True
    return False

def main():
    st.title("Financial DashBoard")
    file_upl = st.file_uploader("Upload your transaction file", type=["csv"])

    if file_upl is not None:
        df = load_trans(file_upl)
        if df is not None:

            dbt_df = df[df["Debit/Credit"] == "Debit"].copy()
            st.session_state.dbt_df = dbt_df.copy()

            # 👇 Tabs created here
            tab1, tab2 = st.tabs(["Expenses(Debit)", "Payments(Credit)"])

            # ===================== TAB 1 (DEBIT) =====================
            with tab1:
                st.subheader("Category Management")
                new_cat = st.text_input("Enter Category Name", key="a")
                add_btn = st.button("Add Category", key="a1")

                if new_cat and add_btn:
                    if new_cat not in st.session_state.categories:
                        st.session_state.categories[new_cat] = []
                        save_cat()
                        st.success("New Category Added")
                        st.rerun()

                st.subheader("Your Expenses")

                editor_df = st.data_editor(
                    st.session_state.dbt_df[["Date", "Details", "Amount", "Category"]],
                    column_config={
                        "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                        "Amount": st.column_config.NumberColumn("Amount", format="%.2f AED"),
                        "Category": st.column_config.SelectboxColumn(
                            "Category",
                            options=list(st.session_state.categories.keys())
                        )
                    },
                    hide_index=True,
                    width='stretch',
                    key="category_editor"
                )

                save_button = st.button("Apply Changes", type="primary")

                if save_button:
                    for idx, row in editor_df.iterrows():
                        new_cat = row["Category"]
                        if new_cat != st.session_state.dbt_df.at[idx, "Category"]:
                            st.session_state.dbt_df.at[idx, "Category"] = new_cat
                            add_keyword_to_cat(new_cat, row["Details"])

                st.subheader("Expense Summary")

                category_totals = st.session_state.dbt_df.groupby("Category")["Amount"].sum().reset_index()
                category_totals = category_totals.sort_values("Amount", ascending=False)

                fig, ax = plt.subplots(1, 2, figsize=(14, 6))
                colors = plt.cm.Set3.colors

                ax[0].pie(
                    category_totals["Amount"],
                    labels=category_totals["Category"],
                    autopct='%1.1f%%',
                    startangle=90,
                    colors=colors,
                    wedgeprops={'edgecolor': 'white', 'linewidth': 1}
                )
                ax[0].set_title("Spending by Category", fontsize=12, fontweight='bold')

                ax[1].bar(
                    category_totals["Category"],
                    category_totals["Amount"],
                    color=colors
                )

                ax[1].set_title("Category-wise Amount", fontsize=12, fontweight='bold')
                ax[1].set_ylabel("Amount")
                ax[1].set_xlabel("Category")
                ax[1].spines[['top', 'right']].set_visible(False)
                ax[1].grid(axis='y', linestyle='--', alpha=0.5)

                plt.setp(ax[1].get_xticklabels(), rotation=45, ha='right')
                plt.tight_layout()

                st.pyplot(fig)

            # ===================== TAB 2 (CREDIT) =====================
            with tab2:
                st.subheader("Category Management")
                new_cat = st.text_input("Enter Category Name", key="a11")
                add_btn = st.button("Add Category", key="a111")

                if new_cat and add_btn:
                    if new_cat not in st.session_state.categories:
                        st.session_state.categories[new_cat] = []
                        save_cat()
                        st.success("New Category Added")
                        st.rerun()

                st.subheader("Your Payments")

                editor_df = st.data_editor(
                    st.session_state.dbt_df[["Date", "Details", "Amount", "Category"]],
                    column_config={
                        "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                        "Amount": st.column_config.NumberColumn("Amount", format="%.2f AED"),
                        "Category": st.column_config.SelectboxColumn(
                            "Category",
                            options=list(st.session_state.categories.keys())
                        )
                    },
                    hide_index=True,
                    width='stretch',
                    key="category_editor"
                )

                save_button = st.button("Apply Changes", type="primary")

                if save_button:
                    for idx, row in editor_df.iterrows():
                        new_cat = row["Category"]
                        if new_cat != st.session_state.dbt_df.at[idx, "Category"]:
                            st.session_state.dbt_df.at[idx, "Category"] = new_cat
                            add_keyword_to_cat(new_cat, row["Details"])

                st.subheader("Expense Summary")

                category_totals = st.session_state.dbt_df.groupby("Category")["Amount"].sum().reset_index()
                category_totals = category_totals.sort_values("Amount", ascending=False)

                fig, ax = plt.subplots(1, 2, figsize=(14, 6))
                colors = plt.cm.Set3.colors

                ax[0].pie(
                    category_totals["Amount"],
                    labels=category_totals["Category"],
                    autopct='%1.1f%%',
                    startangle=90,
                    colors=colors,
                    wedgeprops={'edgecolor': 'white', 'linewidth': 1}
                )
                ax[0].set_title("Spending by Category", fontsize=12, fontweight='bold')

                ax[1].bar(
                    category_totals["Category"],
                    category_totals["Amount"],
                    color=colors
                )

                ax[1].set_title("Category-wise Amount", fontsize=12, fontweight='bold')
                ax[1].set_ylabel("Amount")
                ax[1].set_xlabel("Category")
                ax[1].spines[['top', 'right']].set_visible(False)
                ax[1].grid(axis='y', linestyle='--', alpha=0.5)

                plt.setp(ax[1].get_xticklabels(), rotation=45, ha='right')
                plt.tight_layout()

                st.pyplot(fig)


main()