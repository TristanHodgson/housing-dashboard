from modules import data
import pandas as pd
import branca.colormap as cm
import folium


def get_data(month):
    map_df = data.monthly_for_map(month)
    gdf = data.get_map_geometry()
    merged_gdf = gdf.merge(map_df, on="AreaCode", how="left",
                           suffixes=("_geo", "_sql"))

    if "RegionName_sql" in merged_gdf.columns:
        merged_gdf = merged_gdf.rename(
            columns={"RegionName_sql": "RegionName"})
    merged_gdf["RegionName"] = merged_gdf["RegionName"].fillna(
        merged_gdf["AreaCode"])

    merged_gdf["RoundedPrice"] = merged_gdf["AveragePrice"].map(
        lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
    return merged_gdf


def make_colormap(linear):
    if linear:
        return cm.LinearColormap(
            cm.linear.RdYlBu_11.colors[::-1],
            vmin=0,
            vmax=data.get_max_price(),
            caption="Average House Price (£)",
        )
    else:
        return cm.LinearColormap(
            colors=["#000FFF", "#FFC573", "#FF824C", "#FF4126", "#FF0000"],
            vmin=0,
            vmax=data.get_max_price(),
            caption="Average House Price (£)",
        )

def style_fn(colormap):
    def style(feature):
        price = feature["properties"]["AveragePrice"]
        if price is None:
            return {"fillOpacity": 0.5, "weight": 0.5, "color": "black", "fillColor": "#CCCCCC"}
        return {"fillOpacity": 0.7, "weight": 0.2, "color": "white", "fillColor": colormap(price)}
    return style

def create_map(gdf, colormap):
    m = folium.Map(location=[54.5, -3.2],
                   zoom_start=6, tiles="cartodbpositron")
    if not gdf.empty:
        folium.GeoJson(
            gdf.to_json(),
            style_function=style_fn(colormap),
            tooltip=folium.GeoJsonTooltip(
                fields=["RegionName", "RoundedPrice"],
                aliases=["Area", "Avg Price (£)"]
            ),
        ).add_to(m)
        colormap.add_to(m)
    return m
