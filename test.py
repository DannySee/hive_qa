import sqlalchemy
import pandas as pd
from deta import Deta

sql_server = sqlalchemy.create_engine(f"mssql+pymssql://admin:Magazineapt1@hive-db.ckhwntg3tw7d.us-east-2.rds.amazonaws.com:1433/hive")
deta = Deta('b0nqekpqxrp_8XBkoqzrTjtNjUubNLFTauZ1xTDUTokS')


def get_data(table):
    with sql_server.connect() as connection:
        df = pd.read_sql(f"SELECT VA_NUM,CA_NUM,AGMT_DESC,ASSOCIATE,TEAM_LEAD,TEAM,NOTES,SR,COMPLETED,ERROR,YEAR,PERIOD,WEEK,ACCURACY,COUNT,ACC_DESC,PASS_FAIL FROM {table} ORDER BY PRIMARY_KEY ", connection)
        df.fillna("", inplace=True) 

    return df.astype(str)


def put_task():
    
    db = deta.Base("quality_agreement")
    return db.fetch().items


data = put_task()

print(data)