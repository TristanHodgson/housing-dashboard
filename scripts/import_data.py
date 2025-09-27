import pandas as pd
from sqlalchemy import create_engine
from tqdm.autonotebook import tqdm

engine = create_engine("sqlite:///data/data.sqlite")

csv_file = "data/UK-HPI-full-file-2025-06.csv"
table_name = "hpi_sales"
chunk_size = 50000

# with engine.connect() as connection:
#     connection.execute(f"DROP TABLE IF EXISTS {table_name}")

with pd.read_csv(csv_file, chunksize=chunk_size) as reader:
    for chunk in tqdm(reader):
        chunk["Date"] = pd.to_datetime(chunk["Date"], format="%d/%m/%Y")
        chunk.loc[chunk["AreaCode"] == "E08000039", "AreaCode"] = "E08000019"
        chunk.loc[chunk["AreaCode"] == "E08000038", "AreaCode"] = "E08000016"
        chunk.to_sql(
            table_name,
            con=engine,
            if_exists="append",
            index=False
        )
