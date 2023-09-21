import streamlit as st
import data_handler as db
import config.quality_agreement as qa
import pandas as pd
import page_setup as ps

data_table = "account_assignments"


@st.cache_data()
def pull_data(table):
    with db.sql_server.begin() as connection:
        df = pd.read_sql(f"SELECT * FROM {table} ORDER BY PRIMARY_KEY DESC", connection)
        df.fillna("", inplace=True)

    return df.astype(str)
 

def main():
    st.set_page_config(layout="wide")
    st.title("Account Assignments")
    
    ps.build_tab(data_table, pull_data, date_columns=["TIMESTAMP"], quick_filters=["CUSTOMER", "TEAM_LEAD", "T1_USER", "T2_USER", "T3_USER"])

if __name__ == "__main__":
    main()