import pandas as pd
import sqlalchemy

sql_server =  sqlalchemy.create_engine('mssql+pyodbc://MS248CSSQL01/Pricing_Agreements?driver=SQL+Server')


def get_data(table):
    with sql_server.connect() as connection:
        df = pd.read_sql(f"SELECT * FROM {table} WHERE WEEK = 23 AND YEAR = 2023 ORDER BY PRIMARY_KEY", connection, index_col="PRIMARY_KEY")
        df.fillna("", inplace=True) 

    return df.astype(str)


df = get_data("Agreement_Archive")


for row in df.items():
    print(row[0])