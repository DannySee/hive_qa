import streamlit as st
import data_handler as db
import config.quality_agreement as qa
import pandas as pd
import page_setup as ps

deviated_agreement_table = "hive_Programs"


#@st.cache_data()
def deviated_agreement_data(table):
    with db.sql_server.begin() as connection:
        df = pd.read_sql(f"SELECT * FROM {table} ORDER BY PRIMARY_KEY DESC", connection)
        df.fillna("", inplace=True)

    return df.astype(str)
 

def main():
    st.set_page_config(layout="wide")
    st.title("Deviated Agreements")

    ps.build_tab(deviated_agreement_table, deviated_agreement_data)

if __name__ == "__main__":
    main()