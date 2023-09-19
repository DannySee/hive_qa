import streamlit as st
import pandas as pd
import sqlalchemy
from sqlalchemy import Update, text

sql_server = sqlalchemy.create_engine(f"mssql+pymssql://admin:Magazineapt1@hive-db.ckhwntg3tw7d.us-east-2.rds.amazonaws.com:1433/hive")


def import_file(table, data, data_func, date_columns=None):
    if f"{table}_import" in st.session_state:
        file = st.session_state[f"{table}_import"]

        if file is not None:
            change_df = []

            try:
                data["PRIMARY_KEY"] = data["PRIMARY_KEY"].astype(int)
                data.set_index("PRIMARY_KEY", inplace=True)
                import_df = pd.read_csv(file, index_col="PRIMARY_KEY", dtype=str, keep_default_na=False)
                if date_columns is not None:
                    import_df[date_columns] = import_df[date_columns].apply(pd.to_datetime, errors="coerce")

                change_df = data.compare(import_df)
                print(change_df)

            except Exception as e:
                st.write("CSV in unexpected format. Please check the file, ensure column number/order has not changed, and try again. If this exception should not have been raised, please send the below message to the application admin.")
                st.code(str(e))
                st.markdown("---")
                st.toast("woopsy, that's no good!", icon="🤖")

            if len(change_df) > 0:
                changes = change_df.xs('other', axis=1, level=1)

                for primary_key, row in changes.iterrows():
                    update_dict = {column: row[column] for column in row.index if pd.notna(row[column])}
                    set_clause = ', '.join([f"{column} = :{column}" for column in row.index if pd.notna(row[column])])

                    update_query = text(f"UPDATE {table} SET {set_clause} WHERE PRIMARY_KEY = :primary_key")
                    with sql_server.begin() as connection:
                        result = connection.execute(update_query, {"primary_key": primary_key, **update_dict})

                    print(primary_key)

                st.toast(f"Import Successful: ({len(changes)})", icon="🤖")
                data_func.clear()


def save_updates(table, data, data_func):
    if f"{table}_editor" in st.session_state:
        edited_rows = st.session_state[f"{table}_editor"]["edited_rows"]

        for row, columns in edited_rows.items():
            primary_key = data.loc[row, "PRIMARY_KEY"]

            update_dict = {column: columns[column] for column in columns}
            set_clause = ', '.join([f"{column} = :{column}" for column in columns])
            
            update_query = text(f"UPDATE {table} SET {set_clause} WHERE PRIMARY_KEY = :primary_key")
            with sql_server.begin() as connection:
                result = connection.execute(update_query, {"primary_key": primary_key, **update_dict})

            print(f"saved: {primary_key}")

        data_func.clear()


def filter_data(table, data, data_func, columns):
    return