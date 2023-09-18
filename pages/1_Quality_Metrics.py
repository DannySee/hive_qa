import streamlit as st
import data_handler as db
import config.quality_agreement as qa


def build_editor(table, data):
    st.data_editor(
        data,  
        column_config={
            "PRIMARY_KEY": None
        },
        column_order=qa.column_order,
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


def build_tab(tab, table):
    data = db.get_data(table)

    with tab:
        st.button("Save", on_click=lambda: db.save_updates(table, data), key=f"{table}_save")
        build_editor(table, data)

        st.markdown("---")

        export_button(table, data) 
        st.file_uploader("Import a CSV file:", on_change=lambda: db.import_file(table, data), key=f"{table}_import")
            

def main():
    st.set_page_config(layout="wide")

    st.title("Quality Metrics")
    agreement, inquiry, price_rule = st.tabs(["Agreement Accuracy", "Support Request Timeliness", "Price Rule Accuracy"])

    #tabs = {
    #    agreement: "Dash_Agreement",
    #    inquiry: "Dash_Inquiry",
    #    price_rule: "Dash_PriceRule"
    #}
    #for tab, table in tabs.items():
    #    build_tab(tab, table)
    build_tab(agreement, "Dash_Agreement")

if __name__ == "__main__":
    main()