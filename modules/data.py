from sqlalchemy import create_engine, text
import pandas as pd
import streamlit as st

DB = "sqlite:///data/data.sqlite"
TABLE = "hpi_sales"


@st.cache_resource
def db_engine(path=DB):
    return create_engine(path, future=True)

@st.cache_data
def get_data(table_name=TABLE):
    sql = text(f"""
        SELECT 
            Date, 
            AreaCode,
            CASE
                WHEN COALESCE(SUM(SalesVolume), 0) = 0
                THEN AVG(AveragePrice)
                ELSE SUM(AveragePrice * SalesVolume) / SUM(SalesVolume)
            END AS AvgPrice
        FROM {table_name}
        WHERE Date IS NOT NULL
        GROUP BY Date, AreaCode
        ORDER BY Date
    """)
    
    with db_engine().connect() as con:
        df = pd.read_sql_query(sql, con, parse_dates=["Date"])
    df = df.pivot(index="Date", columns="AreaCode", values="AvgPrice")
    return df

@st.cache_data
def get_area_mapping(table_name=TABLE):
    sql = text(f"""
        SELECT DISTINCT AreaCode, RegionName 
        FROM {table_name} 
        WHERE AreaCode IS NOT NULL
    """)
    with db_engine().connect() as con:
        df = pd.read_sql_query(sql, con)
    df = df.drop_duplicates(subset=["AreaCode"])
    return dict(zip(df.RegionName, df.AreaCode))

@st.cache_data
def get_region_list(table=TABLE):
    sql = text(f"""
        SELECT DISTINCT RegionName
        FROM {table}
        WHERE RegionName IS NOT NULL
    """)
    with db_engine().connect() as con:
        df = pd.read_sql_query(sql, con)
    regions = sorted({str(r).strip() for r in df["RegionName"]})
    return regions