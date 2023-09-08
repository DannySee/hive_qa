import streamlit as st
import pandas as pd
import sqlalchemy

sql_server =  sqlalchemy.create_engine('mssql+pyodbc://MS248CSSQL01/Pricing_Agreements?driver=SQL+Server')


def get_data(table):
    with sql_server.connect() as connection:
        df = pd.read_sql(f"SELECT * FROM {table} WHERE WEEK = 1 ORDER BY PRIMARY_KEY ", connection)
        df.fillna("", inplace=True) 

    return df.astype(str)


def import_file(table, data):
    if f"{table}_import" in st.session_state:
        file = st.session_state[f"{table}_import"]

        if file is not None:
            change_df = []

            try:
                data["PRIMARY_KEY"] = data["PRIMARY_KEY"].astype(int)
                data.set_index("PRIMARY_KEY", inplace=True)
                import_df = pd.read_csv(file, index_col="PRIMARY_KEY", dtype=str, keep_default_na=False)
                change_df = data.compare(import_df)

            except Exception as e:
                st.write("CSV in unexpected format. Please check the file, ensure column number/order has not changed, and try again. If this exception should not have been raised, please send the below message to the application admin.")
                st.code(str(e))
                st.markdown("---")
                st.toast("woopsy, that's no good!", icon="🤖")

            if len(change_df) > 0:
                changes = change_df.xs('other', axis=1, level=1)

                for primary_key, row in changes.iterrows():
                    updates = [f"{column} = '{row[column]}'" for column in row.index if pd.notna(row[column])]
                    update_string = ", ".join(updates)

                    with sql_server.connect() as connection:
                        connection.execute(f"UPDATE {table} SET {update_string} WHERE PRIMARY_KEY = {primary_key}")

                st.toast(f"Import Successful: ({len(changes)})", icon="🤖")
                st.experimental_rerun()


def save_updates(table, data):
    if f"{table}_editor" in st.session_state:
        edited_rows = st.session_state[f"{table}_editor"]["edited_rows"]

        for row, columns in edited_rows.items():
            primary_key = data.loc[row, "PRIMARY_KEY"]
            updates = [f"{column} = '{columns[column]}'" for column in columns]
            update_string = ", ".join(updates)
            
            with sql_server.connect() as connection:
                connection.execute(f"UPDATE {table} SET {update_string} WHERE PRIMARY_KEY = {primary_key}")

                