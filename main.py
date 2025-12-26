import streamlit as st
import pandas as pd
import branca.colormap as cm
import streamlit as st
import pandas as pd
import geopandas as gpd
from arcgis.gis import GIS
import branca.colormap as cm
import folium
from streamlit_folium import st_folium
import numpy as np
import plotly.graph_objects as go


from modules import data, geo_data, line, pca


####################
##### Get Data #####
####################

df = data.get_data().dropna()
mapping = data.get_area_mapping()
months = df.index.unique().sort_values()
regions = data.get_region_list()
time_df = df.transpose()
returns = np.log(df).diff().dropna()
time_returns_df = returns.transpose()
areacode_to_region = {code: name for name, code in mapping.items()}

#####################
##### Streamlit #####
#####################

st.set_page_config(page_title="UK House Price Dashboard", layout="wide")
st.title("UK House Price Dashboard")

vis_tab, analysis_tab = st.tabs(["Visualisation", "Analysis"])

with vis_tab:

    ######################
    ##### Choropleth #####
    ######################

    with st.sidebar:
        selected_regions = st.multiselect(
            "Select regions to compare",
            options=regions,
            default=["England", "North West", "Scotland", "Northern Ireland"])
        selected_areacodes = [mapping[region] for region in selected_regions]


    st.header(f"Prices Map")


    col1, col2 = st.columns([1, 4])

    with col1:
        selected_month = st.select_slider(
            "Select Month",
            options=months,
            value=months[-1],
            format_func=lambda d: d.strftime("%b %Y"))
        linear_color = st.checkbox("Use a linear colormap", value=False)


    colors = (cm.linear.RdYlBu_11.colors[::-1] if linear_color else [
            "#0000FF", "#FFC573", "#FF824C", "#FF4126", "#FF0000"])

    ch_df = df.loc[selected_month]
    ch_df = pd.DataFrame({
        "areacode": ch_df.index,
        "value": ch_df.values,
        "label_area": ch_df.index.map(areacode_to_region),
        "label_value": ch_df.apply(lambda x: f"£{x:,.0f}" if pd.notnull(x) else "No Data")})

    fig = geo_data.create_choropleth(
        ch_df, caption="Average House Price (£)", colors=colors, vmin=0)

    with col2:
        st_folium(fig, width="stretch", height=600)


    #######################
    ##### Line Graphs #####
    #######################

    st.header(f"Line Graph")

    raw_tab, rebased_tab, returns_tab = st.tabs(
        ["Raw Price", "Rebased", "Log Returns"])

    filtered_time_df = time_df.loc[selected_areacodes]

    with raw_tab:
        fig = line.create_line(filtered_time_df, selected_regions)
        st.plotly_chart(fig, width="stretch")

    with rebased_tab:
        col1, col2 = st.columns([1, 4])
        with col1:
            base_month = st.select_slider(
                "Select Base Month",
                options=months[:-1],
                value=months[0],
                format_func=lambda d: d.strftime("%b %Y"),
                key="rebase_month")
        with col2:
            rebased_df = filtered_time_df.loc[:,
                                            filtered_time_df.columns >= base_month]
            base_values = rebased_df[base_month]
            rebased_df = rebased_df.div(base_values, axis=0) * 100

            fig = line.create_line(rebased_df, selected_regions)
            fig.update_yaxes(title="Indexed Prices")
            st.plotly_chart(fig, width="stretch")

    with returns_tab:
        filtered_time_returns_df = time_returns_df.loc[selected_areacodes] * 100
        fig = line.create_line(filtered_time_returns_df, selected_regions)
        fig.update_yaxes(title="Monthly log return (%)", tickformat=".1f")
        fig.update_traces(
            hovertemplate="<b>%{fullData.name}</b>: %{y:.2f}%<extra></extra>")
        st.plotly_chart(fig, width="stretch")


    #######################
    ##### Correlation #####
    #######################

    st.header(f"Correlation Matrix")


    filtered_returns_df = time_returns_df.loc[selected_areacodes]
    corr = filtered_returns_df.T.corr()
    filtered_areacode_to_region = {mapping[region]: region for region in selected_regions}
    corr = corr.rename( index=filtered_areacode_to_region, columns=filtered_areacode_to_region)
    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.index,
        zmin=-1, zmax=1,
        colorscale="RdBu",
        hovertemplate="Corr: %{z:,.3f}<extra></extra>", 
    ))
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, width="stretch")


#######################
#####     PCA     #####
#######################

with analysis_tab:
    st.header(f"Principle Component Analysis")
    num_components = 7
    col1, col2 = st.columns([1, 4])
    with col1:
        pc = st.select_slider(
            "Select Principle Component",
            options=[f"PC{i}" for i in range(1, num_components+1)],
            value="PC1")

    eigenvectors, scree = pca.pca(returns, n=num_components)
    eigenvector = eigenvectors[pc]

    eigenvector["label_area"] = eigenvector["areacode"].map(areacode_to_region)
    eigenvector["label_value"] = eigenvector["value"]

    mx = eigenvector["value"].abs().max()
    fig =  geo_data.create_choropleth(eigenvector, caption=f"{pc} loadings", vmin=-mx, vmax=mx)


    with col2:
        st_folium(fig, width="stretch", height=600)

    st.subheader(f"Scree Plot")


    st.bar_chart(scree, x_label="Component", y_label="Variance")