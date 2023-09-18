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


def put_task(insert):
    
    db = deta.Base("quality_agreement")
    return db.put_many(insert)

def

data = get_data("Dash_Agreement")

count = 1
insert = []
for row in data.iterrows():

    if count % 25 == 0:
        if count > 19100:
            put_task(insert)
        insert = []
        print(count)
        
    insert.append({
        "VA_NUM": row[1]['VA_NUM'],
        "CA_NUM": row[1]['CA_NUM'],
        "AGMT_DESC": row[1]['AGMT_DESC'],
        "ASSOCIATE": row[1]['ASSOCIATE'],
        "TEAM_LEAD": row[1]['TEAM_LEAD'],
        "TEAM": row[1]['TEAM'],
        "NOTES": row[1]['NOTES'],
        "SR": row[1]['SR'],
        "COMPLETED": row[1]['COMPLETED'],
        "ERROR": row[1]['ERROR'],
        "YEAR": row[1]['YEAR'],
        "PERIOD": row[1]['PERIOD'],
        "WEEK": row[1]['WEEK'],
        "ACCURACY": row[1]['ACCURACY'],
        "COUNT": row[1]['COUNT'],
        "ACC_DESC": row[1]['ACC_DESC'],
        "PASS_FAIL": row[1]['PASS_FAIL']
    })

    if count == len(data):
        put_task(insert)
        print("last one")

    count += 1