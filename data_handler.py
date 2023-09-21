import streamlit as st
import pandas as pd
import sqlalchemy
from sqlalchemy import Update, text

sql_server = sqlalchemy.create_engine(f"mssql+pymssql://admin:Magazineapt1@hive-db.ckhwntg3tw7d.us-east-2.rds.amazonaws.com:1433/hive")


def import_update(table, data, import_df):
    import_df = import_df[import_df.index.isin(data.index)] 
    data = data[data.index.isin(import_df.index)]
    updates = data.compare(import_df)
    print(updates)

    if len(updates) > 0: 
        updates = updates.xs('other', axis=1, level=1)
    
        for primary_key, row in data.iterrows():
            update_dict = {column: row[column] for column in row.index if pd.notna(row[column])}
            set_clause = ', '.join([f"{column} = :{column}" for column in row.index if pd.notna(row[column])])
            update_query = text(f"UPDATE {table} SET {set_clause} WHERE PRIMARY_KEY = :primary_key")

            with sql_server.begin() as connection:
                connection.execute(update_query, {"primary_key": primary_key, **update_dict})

    return len(updates)


def import_insert(table, data):
    data = data[data.index == ""]
    print(data)

    if len(data) > 0:
        for primary_key, row in data.iterrows():
            insert_dict = {column: row[column] for column in row.index}
            insert_clause = ', '.join([f":{column}" for column in row.index])
            insert_columns = ', '.join([f"{column}" for column in row.index])
            insert_query = text(f"INSERT INTO {table} ({insert_columns}) VALUES ({insert_clause})")
            
            with sql_server.begin() as connection:
                connection.execute(insert_query, insert_dict)
        
    return len(data)


def import_delete(table, data, import_df):
    data = data[data.index.isin(import_df.index) == False]
    print(data)

    if len(data) > 0:
        keys = data.index.tolist()
        delete_query = text(f"DELETE FROM {table} WHERE PRIMARY_KEY IN :primary_key")

        with sql_server.begin() as connection:
            connection.execute(delete_query, {"primary_key": keys})

    return len(data)


def import_file(table, data, data_func, date_columns=None):
    if f"{table}_import" in st.session_state:
        file = st.session_state[f"{table}_import"]

        if file is not None:
            updates = 0
            inserts = 0
            deletes = 0

            try:
                data.set_index("PRIMARY_KEY", inplace=True)
                import_df = pd.read_csv(file, dtype=str, keep_default_na=False)
                import_df.set_index("PRIMARY_KEY", inplace=True)
                
                if date_columns is not None: 
                    import_df[date_columns] = import_df[date_columns].apply(pd.to_datetime, errors="coerce")
                    
                updates = import_update(table, data, import_df)
                inserts = import_insert(table, import_df)
                deletes = import_delete(table, data, import_df)

            except Exception as e:
                st.write("Import inclomplete: CSV in unexpected format. Please check the file, ensure column number/order has not changed, and try again. If this exception should not have been raised, please send the below message to the application admin.")
                st.code(str(e))
                st.markdown("---")
                st.toast("woopsy, something went wrong.", icon="🤖")

            if sum([updates, inserts, deletes]) > 0:
                st.toast(f"""Total Imports: ({sum([updates, inserts, deletes])})- Update: ({updates}), Insert: ({inserts}), Delete: ({deletes})""", icon="🤖")
                data_func.clear()
                
            else:
                st.toast("No changes detected.", icon="🤖")
            

def save_updates(table, data, data_func):
    if f"{table}_editor" in st.session_state:
        edited_rows = st.session_state[f"{table}_editor"]["edited_rows"]

        for row, columns in edited_rows.items():
            primary_key = data.loc[row, "PRIMARY_KEY"]

            update_dict = {column: columns[column] for column in columns}
            set_clause = ', '.join([f"{column} = :{column}" for column in columns])
            
            update_query = text(f"UPDATE {table} SET {set_clause} WHERE PRIMARY_KEY = :primary_key")
            with sql_server.begin() as connection:
                connection.execute(update_query, {"primary_key": primary_key, **update_dict})

        if len(edited_rows) > 0:
            st.toast(f"Update Successful: ({len(edited_rows)})",icon="🤖")
            data_func.clear()
            
        else:
            st.toast("No changes detected.", icon="🤖")