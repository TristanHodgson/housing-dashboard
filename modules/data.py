from sqlalchemy import create_engine, text
import pandas as pd
import geopandas as gpd

import streamlit as st
from arcgis.gis import GIS

from math import ceil
from pathlib import Path

DB = "sqlite:///data/data.sqlite"
TABLE = "hpi_sales"
GEOM_PATH = Path("data/uk_boundaries.parquet")
MIN_YEAR = 1995
MIN_DATE = pd.Timestamp(f"{MIN_YEAR}-01-01")


@st.cache_resource
def db_engine():
    return create_engine(DB, future=True)


@st.cache_data
def get_date_bounds(regions=None, MIN_DATE=MIN_DATE, TABLE=TABLE):
    if not regions:
        sql = f"""
            SELECT MIN(Date) AS min_d,
                   MAX(Date) AS max_d
            FROM {TABLE}
            WHERE Date IS NOT NULL
        """
        with db_engine().connect() as con:
            row = con.execute(text(sql)).mappings().first()
    else:
        params = ({f"r{i}": r for i, r in enumerate(regions)})
        regions = ", ".join([f":r{i}" for i in range(len(regions))])
        sql = f"""
            SELECT
                MAX(x.min_d) AS min_d,
                MIN(x.max_d) AS max_d
            FROM (
                SELECT RegionName,
                       MIN(Date) AS min_d,
                       MAX(Date) AS max_d
                FROM {TABLE}
                WHERE date IS NOT NULL
                  AND RegionName IN ({regions})
                GROUP BY RegionName
            ) x
        """
        with db_engine().connect() as con:
            row = con.execute(text(sql), params).mappings().first()

    min_date = pd.to_datetime(row["min_d"])
    max_date = pd.to_datetime(row["max_d"])
    min_date = max(min_date, MIN_DATE).normalize().replace(day=1)
    max_date = max_date.normalize().replace(day=1)
    if min_date > max_date:
        return (None, None)
    return (min_date, max_date)


@st.cache_data
def get_max_price(MIN_YEAR=MIN_YEAR, TABLE=TABLE):
    sql = f"""
    SELECT max(AveragePrice) as m
    FROM {TABLE}
    WHERE AveragePrice IS NOT NULL and Date IS NOT NULL and Date >= '{MIN_YEAR}-01-01'
    """
    with db_engine().connect() as con:
        row = con.execute(text(sql)).mappings().first()
    x = pd.to_numeric(row["m"])
    if pd.isna(x):
        return 0
    x = max(0, x)
    return ceil(x / 100000) * 100000


@st.cache_data
def monthly_for_map(month: pd.Timestamp, TABLE=TABLE) -> pd.DataFrame:
    m = pd.Timestamp(month).normalize().replace(day=1)
    ym = m.strftime("%Y-%m")
    sql = text(f"""
            SELECT
            AreaCode,
            MIN(RegionName) AS RegionName,
            CASE
                WHEN COALESCE(SUM(SalesVolume), 0) = 0
                THEN AVG(AveragePrice)
                ELSE SUM(AveragePrice * SalesVolume) / SUM(SalesVolume)
            END AS AveragePrice
            FROM {TABLE}
            WHERE strftime('%Y-%m', Date) = :ym
            GROUP BY AreaCode
        """)
    with db_engine().connect() as con:
        df = pd.read_sql_query(sql, con, params={"ym": ym})
    df["AveragePrice"] = pd.to_numeric(df["AveragePrice"], errors="coerce")
    return df


@st.cache_data
def get_map_geometry(GEOM_PATH=GEOM_PATH) -> gpd.GeoDataFrame:
    if GEOM_PATH.exists():
        return gpd.read_parquet(GEOM_PATH)
    gis = GIS()
    item = gis.content.search(
        query="Local Authority Districts (December 2024) Boundaries UK BUC",
        item_type="Feature Layer"
    )[0]
    sdf = item.layers[0].query(as_df=True)
    sdf = sdf.rename(columns={"LAD24NM": "RegionName", "LAD24CD": "AreaCode"})

    gdf = gpd.GeoDataFrame(sdf, geometry="SHAPE").rename(
        columns={"SHAPE": "geometry"})
    gdf = gdf.set_geometry("geometry")
    gdf.crs = "EPSG:27700"
    gdf = gdf.to_crs(epsg=4326)

    GEOM_PATH.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(GEOM_PATH)
    return gdf


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


@st.cache_data
def get_region_data(table=TABLE, min_year=MIN_YEAR, regions=(), include_uk: bool = False):
    if not regions and not include_uk:
        return pd.DataFrame()
    regions = list(dict.fromkeys(list(regions) +
                   (["United Kingdom"] if include_uk else [])))
    params = {"min_date": f"{min_year}-01-01"}
    params.update({f"r{i}": r for i, r in enumerate(regions)})
    regions = ", ".join([f":r{i}" for i in range(len(regions))])
    sql = text(f"""
        SELECT
            Date,
            RegionName,
            CASE
                WHEN COALESCE(SUM(SalesVolume), 0) = 0
                THEN AVG(AveragePrice)
                ELSE SUM(AveragePrice * SalesVolume) / SUM(SalesVolume)
            END AS AveragePrice
        FROM {table}
        WHERE Date >= :min_date
          AND RegionName IN ({regions})
        GROUP BY Date, RegionName
        ORDER BY Date
        """)
    with db_engine().connect() as con:
        df = pd.read_sql_query(sql, con, params=params)
    if df.empty:
        return pd.DataFrame()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    return df.pivot(index="Date", columns="RegionName", values="AveragePrice").sort_index()


@st.cache_data
def get_available_months(TABLE=TABLE, MIN_YEAR=MIN_YEAR):
    sql = f"""
        SELECT DISTINCT Date
        FROM {TABLE}
        WHERE Date IS NOT NULL AND Date >= '{MIN_YEAR}-01-01'
        ORDER BY Date"""
    with db_engine().connect() as con:
        dates = pd.read_sql_query(sql, con)["Date"]
    dates = pd.to_datetime(dates, errors="coerce")
    dates = dates.dropna().sort_values().unique()
    return [pd.Timestamp(d).normalize().replace(day=1) for d in dates]
