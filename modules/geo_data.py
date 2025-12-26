import streamlit as st
import pandas as pd
import geopandas as gpd
from arcgis.gis import GIS
import branca.colormap as cm
import folium
from streamlit_folium import st_folium



from pathlib import Path

GEOM_PATH = Path("data/uk_boundaries.parquet")



@st.cache_data
def get_geography(path: Path = GEOM_PATH):
    if path.exists():
        return gpd.read_parquet(path)
    gis = GIS()
    search_results = gis.content.search(
        query="Local Authority Districts (December 2024) Boundaries UK BUC",
        item_type="Feature Layer")
    
    if not search_results:
        raise RuntimeError("Could not find the UK Local Authority boundaries on ArcGIS.")

    item = search_results[0]
    sdf = item.layers[0].query(as_df=True)
    sdf = sdf.rename(columns={"LAD24CD": "AreaCode"})
    
    gdf = gpd.GeoDataFrame(sdf, geometry="SHAPE")
    gdf = gdf.set_geometry("geometry")
    gdf.crs = "EPSG:27700"
    gdf = gdf.to_crs(epsg=4326)
    gdf = gdf[["AreaCode", "geometry"]]

    path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(path)
    return gdf


def create_choropleth(data_df, caption, colors=None, vmin=None, vmax=None):
    gdf = get_geography()
    merged = gdf.merge(
        data_df,
        left_on="AreaCode",
        right_on="areacode",
        how="left"
    )

    if vmin == None:
        vmin = merged["value"].min()
    if vmax == None:
        vmax = merged["value"].max()

    if colors is None:
        colors = cm.linear.RdYlBu_11.colors[::-1]
    colormap = cm.LinearColormap(
        colors=colors,
        vmin=vmin,
        vmax=vmax,
        caption=caption)
    def style_fn(feature):
        val = feature["properties"]["value"]
        if val is None or pd.isna(val):
            return {"fillColor": "#CCCCCC", "color": "black", "weight": 0.5, "fillOpacity": 0.5}
        return {"fillColor": colormap(val), "color": "white", "weight": 0.2, "fillOpacity": 0.7}
    
    m = folium.Map(
        location=[54.5, -3.5], 
        zoom_start=6, 
        tiles="cartodbpositron")
    
    folium.GeoJson(
        merged.to_json(),
        style_function=style_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=["label_area", "label_value"],
            aliases=["Area:", "Value:"],
            localize=True,
            sticky=False)).add_to(m)
    colormap.add_to(m)
    return m


