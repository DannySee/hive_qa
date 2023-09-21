import streamlit as st
import data_handler as db
import config.quality_agreement as qa
import pandas as pd
import page_setup as ps

data_table = "deviated_agreements"


@st.cache_data()
def pull_data(table):
    with db.sql_server.begin() as connection:
        df = pd.read_sql(f"SELECT * FROM {table} ORDER BY PRIMARY_KEY DESC", connection)
        df.fillna("", inplace=True)

    return df.astype(str)
 

def main():
    st.set_page_config(layout="wide")
    st.title("Deviated Agreements")

    ps.build_tab(data_table, pull_data, ['START_DATE','END_DATE','TIMESTAMP'])

if __name__ == "__main__":
    main()