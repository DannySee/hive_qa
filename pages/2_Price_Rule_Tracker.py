import streamlit as st
import data_handler as db
import config.quality_agreement as qa
import pandas as pd
import page_setup as ps

price_rule_table = "PR_Master"


st.cache_data()
def price_rule_tracker_data(table):
    with db.sql_server.begin() as connection:
        df = pd.read_sql(f"SELECT * FROM {table} ORDER BY PRIMARY_KEY DESC", connection)
        df.fillna("", inplace=True)

    return df.astype(str)
 

def main():
    st.set_page_config(layout="wide")
    st.title("Price Rule Tracker")

    ps.build_tab(price_rule_table, price_rule_tracker_data)

if __name__ == "__main__":
    main()