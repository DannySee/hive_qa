import streamlit as st
import data_handler as db
import config.quality_agreement as qa
import pandas as pd
import page_setup as ps

account_assignments_table = "account_assignments"
customer_profile_table = "customer_profile"
deviated_agreements_table = "deviated_agreements"
deviation_loads_table = "deviation_loads"


@st.cache_data()
def account_assignments_data(table):
    with db.sql_server.begin() as connection:
        df = pd.read_sql(f"SELECT * FROM {table} ORDER BY PRIMARY_KEY DESC", connection)
        df.fillna("", inplace=True)

    return df.astype(str)


@st.cache_data()
def customer_profile_data(table):
    with db.sql_server.begin() as connection:
        df = pd.read_sql(f"SELECT * FROM {table} ORDER BY PRIMARY_KEY DESC", connection)
        df.fillna("", inplace=True)

    return df.astype(str)


@st.cache_data()
def deviated_agreements_data(table):
    with db.sql_server.begin() as connection:
        df = pd.read_sql(f"SELECT * FROM {table} ORDER BY PRIMARY_KEY", connection)
        df.fillna("", inplace=True)

    return df.astype(str)


@st.cache_data()
def deviation_loads_data(table):
    with db.sql_server.begin() as connection:
        df = pd.read_sql(f"SELECT * FROM {table} ORDER BY PRIMARY_KEY DESC", connection)
        df.fillna("", inplace=True)

    return df.astype(str)
 

def main():
    st.set_page_config(layout="wide")
    st.title("Hive: Deviated Agreements Team")

    with st.sidebar:
        st.title("Deviated Agreements")
        st.caption("_Note: Unsaved changes will be lost when switching pages._")
        page = st.selectbox("Select Page", label_visibility="collapsed",options=["Account Assignments",
                                                                                "Customer Profile", 
                                                                                "Deviated Agreements", 
                                                                                "Deviation Loads"])
        st.divider()

    if page == "Account Assignments":
        st.write("_Account Assignments_")
        ps.build_tab(account_assignments_table,
                     account_assignments_data,
                     date_columns=['TIMESTAMP'],
                     quick_filters=['CUSTOMER','TEAM_LEAD','T1_USER','T2_USER','T3_USER'])

    elif page == "Customer Profile":
        st.write("_Customer Profile_")
        ps.build_tab(customer_profile_table, 
                     customer_profile_data,
                     date_columns=['TIMESTAMP'],
                     quick_filters=['CUSTOMER','ALT_NAME','T1_USER','T2_USER','T3_USER'])

    elif page == "Deviated Agreements":
        st.write("_Deviated Agreements_")
        ps.build_tab(deviated_agreements_table, 
                     deviated_agreements_data, 
                     date_columns=['START_DATE','END_DATE','TIMESTAMP'], 
                     quick_filters=['CUSTOMER','PROGRAM','T1_USER','T2_USER','T3_USER'])
        
    elif page == "Deviation Loads":
        st.write("_Deviation Loads_")
        ps.build_tab(deviation_loads_table, 
                     deviation_loads_data, 
                     date_columns=['TIMESTAMP'], 
                     quick_filters=['CUSTOMER','PROGRAM','T1_USER','T2_USER','T3_USER'])


if __name__ == "__main__":
    main()