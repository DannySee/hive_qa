import streamlit as st
import data_handler as db


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


def build_filters(table, data, quick_filters=None):
    columns = data.columns.tolist()

    with st.expander("All Filters", expanded=False):
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

    if quick_filters:
        with st.sidebar:
            st.markdown("### Quick Filters")
            st.caption("_Note: Unsaved changes will be lost when filters are applied._")
            
            for column in quick_filters:
                st.multiselect(
                    column,
                    data[column].unique().tolist(),
                    [],
                    key=f"{table}_{column}_quick_filter"
                )


def apply_filters(table, data):
    columns = data.columns.tolist()

    for column in columns:
        if column != "PRIMARY_KEY":
            if f"{table}_{column}_filter" in st.session_state:
                data = data[data[column].str.contains(st.session_state[f"{table}_{column}_filter"], case=False, na=False)]
            if f"{table}_{column}_quick_filter" in st.session_state and st.session_state[f"{table}_{column}_quick_filter"] != []:
                data = data[data[column].isin(st.session_state[f"{table}_{column}_quick_filter"])]

    return data


def build_tab(table, data_func, date_columns=None, quick_filters=None):
    data = data_func(table)
    build_filters(table, data, quick_filters)
    
    data = apply_filters(table, data)
    build_editor(table, data)

    st.button("Save Changes", on_click=lambda: db.save_updates(table, data, data_func), key=f"{table}_save")

    st.markdown("---")

    export_button(table, data) 
    st.file_uploader("Import a CSV file:", on_change=lambda: db.import_file(table, data, data_func, date_columns), key=f"{table}_import")
        