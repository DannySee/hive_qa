import streamlit as st
import data_handler as db
import config.quality_agreement as qa
import pandas as pd


@st.cache_data()
def agreement_data():
    with db.sql_server.begin() as connection:
        df = pd.read_sql(f"SELECT * FROM quality_agreement ORDER BY PRIMARY_KEY DESC", connection)
        df.fillna("", inplace=True)

    return df.astype(str)


@st.cache_data()
def price_rule_data():
    with db.sql_server.begin() as connection:
        df = pd.read_sql("""
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

                FROM Dash_PriceRule 
                
                ORDER BY PRIMARY_KEY
            """, 
            connection
        )
        df.fillna("", inplace=True)

    return df.astype(str)


@st.cache_data()
def inquiry_data():
    with db.sql_server.begin() as connection:
        df = pd.read_sql(f"SELECT * FROM Dash_Inquiry ORDER BY PRIMARY_KEY", connection)
        df.fillna("", inplace=True)

    return df.astype(str)


def build_editor(table, data):
    st.data_editor(
        data,  
        column_config={
            "PRIMARY_KEY": None
        },
        num_rows="fixed",
        hide_index=True,
        key=f"{table}_editor",
    )


def export_button(table, data):
    csv = data.set_index("PRIMARY_KEY").to_csv().encode('utf-8')

    st.download_button(     
        label="Export Data",
        data=csv,
        file_name=f"{table}.csv",
        mime="text/csv",
        key=f"{table}_export"
    )


def clear_filters(table, columns):
    for column in columns:
        if column != "PRIMARY_KEY":
            st.session_state[f"{table}_{column}_filter"] = ""


def build_filters(table, data):

    columns = data.columns.tolist()

    with st.expander("Filters", expanded=False):
        st.caption("_Note: Unsaved changes will be lost when filters are applied._")

        col1, col2, col3, col4, col5, col6, col7 = st. columns(7)
        cols = [col1, col2, col3, col4, col5, col6, col7]
        col_count = 0

        for column in columns:
            if column != "PRIMARY_KEY":
                with cols[col_count]:
                    st.text_input(
                        column,
                        "",
                        key=f"{table}_{column}_filter",
                    )
                col_count = (col_count + 1) if col_count < 6 else 0
            
        col1.button("Clear Filters", on_click=lambda: clear_filters(table, columns), key=f"{table}_clear_filters")


def apply_filters(table, data):
    
    columns = data.columns.tolist()

    for column in columns:
        if column != "PRIMARY_KEY":
            if f"{table}_{column}_filter" in st.session_state:
                data = data[data[column].str.contains(st.session_state[f"{table}_{column}_filter"], case=False, na=False)]

    return data


def build_tab(table, data_func, date_columns=None):

    data = data_func()
    
    build_filters(table, data)
    data = apply_filters(table, data)
    build_editor(table, data)
    st.button("Save Changes", on_click=lambda: db.save_updates(table, data, data_func), key=f"{table}_save")

    st.markdown("---")

    export_button(table, data) 
    st.file_uploader("Import a CSV file:", on_change=lambda: db.import_file(table, data, data_func, date_columns), key=f"{table}_import")
        

def main():
    st.set_page_config(layout="wide")

    st.title("Quality Metrics")
    agreement, inquiry, price_rule = st.tabs(["Agreement Accuracy", "Support Request Timeliness", "Price Rule Accuracy"])

    with agreement:
        build_tab("quality_agreement", agreement_data)

    with inquiry:
        build_tab("Dash_Inquiry", inquiry_data, ["OPENED","CLOSED"])
    
    with price_rule:
        build_tab("Dash_PriceRule", price_rule_data, ["APP_DATE"])


if __name__ == "__main__":
    main()