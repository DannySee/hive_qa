import streamlit as st
import data_handler as db
import config.quality_agreement as qa
import pandas as pd
import page_setup as ps

agreement_table = "quality_agreement"
inquiry_table = "quality_inquiry"
price_rule_table = "quality_price_rule"


@st.cache_data()
def agreement_data(table):
    with db.sql_server.begin() as connection:
        df = pd.read_sql(f"SELECT * FROM {table} ORDER BY PRIMARY_KEY DESC", connection)
        df.fillna("", inplace=True)

    return df.astype(str)


@st.cache_data()
def price_rule_data(table):
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
def inquiry_data(table):
    with db.sql_server.begin() as connection:
        df = pd.read_sql(f"SELECT * FROM {table} ORDER BY PRIMARY_KEY", connection)
        df.fillna("", inplace=True)

    return df.astype(str)
 

def main():
    st.set_page_config(layout="wide")
    st.title("Quality Metrics")
    
    agreement, inquiry, price_rule = st.tabs(["Agreement Accuracy", "Support Request Timeliness", "Price Rule Accuracy"])

    with agreement:
        ps.build_tab(agreement_table, agreement_data)

    with inquiry:
        ps.build_tab(inquiry_table, inquiry_data, ["OPENED","CLOSED"])
    
    with price_rule:
        ps.build_tab(price_rule_table, price_rule_data, ["APP_DATE"])


if __name__ == "__main__":
    main()