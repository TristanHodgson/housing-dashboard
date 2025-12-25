from modules import data
import pandas as pd
import branca.colormap as cm
import folium


def prepare_gdf(value_df, value_col, label_col, value_fmt, join_col="AreaCode"):
    gdf = data.get_map_geometry()
    merged = gdf.merge(
        value_df,
        on=join_col,
        how="left",
        suffixes=("_geo", "_val"),
    )
    if label_col == join_col:
        merged["RegionLabel"] = merged[label_col]
    else:
        val_label = f"{label_col}_val"
        geo_label = f"{label_col}_geo"
        if val_label in merged.columns:
            merged["RegionLabel"] = merged[val_label]
        elif geo_label in merged.columns:
            merged["RegionLabel"] = merged[geo_label]
        else:
            merged["RegionLabel"] = merged[join_col]
    merged["value"] = merged[value_col]
    merged["value_fmt"] = merged["value"].map(value_fmt)
    merged["ValueLabel"] = merged["value_fmt"]
    return merged






def make_colormap(vmin,vmax,colors,caption: str):
    return cm.LinearColormap(
        colors=colors,
        vmin=vmin,
        vmax=vmax,
        caption=caption,
    )


def style_fn(colormap):
    def style(feature):
        value = feature["properties"]["Value"]
        if value is None:
            return {
                "fillOpacity": 0.5,
                "weight": 0.5,
                "color": "black",
                "fillColor": "#CCCCCC",
            }
        return {
            "fillOpacity": 0.7,
            "weight": 0.2,
            "color": "white",
            "fillColor": colormap(value),
        }
    return style


def create_map(gdf, colormap):
    m = folium.Map(
        location=[54.5, -3.2],
        zoom_start=6,
        tiles="cartodbpositron")
    if not gdf.empty:
        folium.GeoJson(
            gdf.to_json(),
            style_function=style_fn(colormap),
            tooltip=folium.GeoJsonTooltip(
                fields=["RegionLabel", "ValueLabel"],
                aliases=["Area", "Value"],
            ),
        ).add_to(m)
        colormap.add_to(m)

    return m
