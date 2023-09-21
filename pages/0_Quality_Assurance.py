import streamlit as st
import data_handler as db
import config.quality_agreement as qa
import pandas as pd
import page_setup as ps

price_rule_approval_table = "price_rule_approval_tracker"
quality_agreement_table = "quality_agreement"
quality_inquiry_table = "quality_inquiry"
quality_price_rule_table = "quality_price_rule"


@st.cache_data()
def quality_agreement_data(table):
    with db.sql_server.begin() as connection:
        df = pd.read_sql(f"SELECT * FROM {table} ORDER BY PRIMARY_KEY DESC", connection)
        df.fillna("", inplace=True)

    return df.astype(str)


@st.cache_data()
def quality_price_rule_data(table):
    with db.sql_server.begin() as connection:
        df = pd.read_sql(f"""
                SELECT 
                PRIMARY_KEY, 
                CUSTOMER, 
                DESCRIPTION, 
                NAME, 
                ASSOCIATE, 
                TEAM_LEAD, 
                APP_DATE, 
                YEAR, 
                PERIOD, 
                WEEK, 
                CAST(GRADE*100 AS INT) AS GRADE, 
                PASS_FAIL 

                FROM {table} 
                
                ORDER BY PRIMARY_KEY
            """, 
            connection
        )
        df.fillna("", inplace=True)

    return df.astype(str)


@st.cache_data()
def quality_inquiry_data(table):
    with db.sql_server.begin() as connection:
        df = pd.read_sql(f"SELECT * FROM {table} ORDER BY PRIMARY_KEY", connection)
        df.fillna("", inplace=True)

    return df.astype(str)


@st.cache_data()
def price_rule_approval_data(table):
    with db.sql_server.begin() as connection:
        df = pd.read_sql(f"SELECT * FROM {table} ORDER BY PRIMARY_KEY DESC", connection)
        df.fillna("", inplace=True)

    return df.astype(str)
 

def main():
    st.set_page_config(layout="wide")
    st.title("Hive: Quality Assurance Team")

    with st.sidebar:
        st.title("Quality Assurance")
        st.caption("_Note: Unsaved changes will be lost when switching pages._")
        page = st.selectbox("Select Page", label_visibility="collapsed",options=["Price Rule Approval",
                                                                                "Quality: Agreement", 
                                                                                "Quality: Inquiry", 
                                                                                "Quality: Price Rule"])
        st.divider()

    if page == "Price Rule Approval":
        st.write("_Price Rule Approval Tracker_")
        ps.build_tab(price_rule_approval_table, 
                     price_rule_approval_data, 
                     date_columns=['APP_DATE','VERSION_DATE','ORIG_MOD','ADD_MOD','SUBMIT_DATE','EXP_DATE','ADJ_DATE'],
                     quick_filters=['CUSTOMER','CONCEPT','PRICE_RULE','APPROVER','SR'])

    elif page == "Quality: Agreement":
        st.write("_Quality Metrics: Agreements Entry_")
        ps.build_tab(quality_agreement_table, 
                     quality_agreement_data,
                     quick_filters=['VA_NUM','CA_NUM','SR','PERIOD','WEEK'])

    elif page == "Quality: Inquiry":
        st.write("_Quality Metrics: Inquiry Timeliness_")
        ps.build_tab(quality_inquiry_table, 
                     quality_inquiry_data, 
                     date_columns=["OPENED","CLOSED"],
                     quick_filters=['ASSOCIATE','TEAM_LEAD','SR','PERIOD','WEEK'])

    elif page == "Quality: Price Rule":
        st.write("_Quality Metrics: Price Rule Accuracy_")
        ps.build_tab(quality_price_rule_table, 
                     quality_price_rule_data, 
                     date_columns=['APP_DATE'],
                     quick_filters=['ASSOCIATE','CUSTOMER','NAME','PERIOD','WEEK'])


if __name__ == "__main__":
    main()