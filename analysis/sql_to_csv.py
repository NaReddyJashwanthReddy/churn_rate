from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import os

load_dotenv()

username = os.getenv("USER_NAME")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
port = os.getenv("PORT")
service_name = os.getenv("SERVICE_NAME")

engine = create_engine(f'oracle+cx_oracle://{username}:{password}@{host}:{port}/?service_name={service_name}')

query = "SELECT * FROM churn_analytics_data"
df = pd.read_sql(query, engine)

df.to_csv(r'../data/churn_analytics_data.csv', index=False)

print("Data has been successfully exported to churn_analytics_data.csv")