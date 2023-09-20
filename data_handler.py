import streamlit as st
import pandas as pd
import sqlalchemy
from sqlalchemy import Update, text

sql_server = sqlalchemy.create_engine(f"mssql+pymssql://admin:Magazineapt1@hive-db.ckhwntg3tw7d.us-east-2.rds.amazonaws.com:1433/hive")


def import_update(table, data):
    for primary_key, row in data.iterrows():
        update_dict = {column: row[column] for column in row.index if pd.notna(row[column])}
        set_clause = ', '.join([f"{column} = :{column}" for column in row.index if pd.notna(row[column])])

        update_query = text(f"UPDATE {table} SET {set_clause} WHERE PRIMARY_KEY = :primary_key")
        with sql_server.begin() as connection:
            connection.execute(update_query, {"primary_key": primary_key, **update_dict})


def insert_data(table, data):
    for primary_key, row in data.iterrows():
        insert_dict = {column: row[column] for column in row.index}
        insert_clause = ', '.join([f":{column}" for column in row.index])
        insert_columns = ', '.join([f"{column}" for column in row.index])

        insert_query = text(f"INSERT INTO {table} ({insert_columns}) VALUES ({insert_clause})")
        print(insert_clause)
        with sql_server.begin() as connection:
            connection.execute(insert_query, insert_dict)


def import_file(table, data, data_func, date_columns=None):
    if f"{table}_import" in st.session_state:
        file = st.session_state[f"{table}_import"]

        if file is not None:
            change_df = []
            status = False

            try:
                data.set_index("PRIMARY_KEY", inplace=True)

                import_df = pd.read_csv(file, index_col="PRIMARY_KEY", dtype=str, keep_default_na=False)
                if date_columns is not None:
                    import_df[date_columns] = import_df[date_columns].apply(pd.to_datetime, errors="coerce")


                ##############################UPDATES################################
                import_update_df = import_df[import_df.index.isin(data.index)] 
                data_update = data[data.index.isin(import_df.index)]
                change_df = data_update.compare(import_update_df)
                if len(change_df) > 0: 
                    updates = change_df.xs('other', axis=1, level=1)
                    import_update(table, updates)
                    status = True

                print(f"updates {change_df} {status}")
                ##############################UPDATES################################

                ##############################INSERTS################################
                import_insert = import_df[import_df.index == ""]
                if len(import_insert) > 0:
                    insert_data(table, import_insert)
                    status = True

                print(f"inserts {import_insert}")
                ##############################INSERTS################################

                ##############################DELETES################################
                data_delete = data[data.index.isin(import_df.index) == False]
                print(f"deletes {data_delete}")
                ##############################DELETES################################

                
                

            except Exception as e:
                st.write("CSV in unexpected format. Please check the file, ensure column number/order has not changed, and try again. If this exception should not have been raised, please send the below message to the application admin.")
                st.code(str(e))
                st.markdown("---")
                st.toast("woopsy, that's no good!", icon="🤖")


            if status:

                st.toast(f"Import Successful: ()", icon="🤖")
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