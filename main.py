import pandas as pd

import streamlit as st
from streamlit_folium import st_folium

import numpy as np
import plotly.graph_objects as go


from modules import data, line, rebase
from modules import choropleth as ch


from math import ceil
from pathlib import Path

DB = "sqlite:///data/data.sqlite"
TABLE = "hpi_sales"
GEOM_PATH = Path("data/uk_boundaries.parquet")
MIN_YEAR = 1995
MIN_DATE = pd.Timestamp(f"{MIN_YEAR}-01-01")

st.set_page_config(page_title="UK House Price Dashboard", layout="wide")
st.title("UK House Price Dashboard")

with st.sidebar:
    regions = data.get_region_list()
    countries = [x for x in ["England", "Wales",
                             "Scotland", "Northern Ireland"] if x in regions]
    selected_regions = st.multiselect(
        "Select regions to compare",
        options=regions,
        default=countries,
    )


map_tab, line_tab, rebase_tab, corr_tab = st.tabs(["Map", "Line Graph", "Rebased", "Correlation"])

with map_tab:
    st.header("Choropleth Map")
    col1, col2 = st.columns([1, 4])
    with col1:
        min_month, max_month = data.get_date_bounds()
        months = data.get_available_months()
        month = st.select_slider(
            "Select Month",
            options=months,
            value=months[-1],
            format_func=lambda d: d.strftime("%b %Y"),
        )
        linear_colormap = st.checkbox("Use a linear colormap", value=False)

    with col2:
        gdf = ch.get_data(month)
        colormap = ch.make_colormap(linear_colormap)
        st_folium(ch.create_map(gdf, colormap), use_container_width=True, height=800)

with line_tab:
    st.header("Prices over time")
    region_data = data.get_region_data(
        regions=tuple(selected_regions), include_uk=True)
    if region_data.empty:
        st.info("No data available for the selected regions")
    else:
        fig = line.create_line_graph(region_data, selected_regions)
        st.plotly_chart(fig, use_container_width=True,
                        theme="streamlit", config={"scrollZoom": False})

        st.subheader("Latest average prices")
        columns = st.columns(max(1, len(selected_regions)))
        for i, (r, v, p) in enumerate(line.perf_metrics(region_data, selected_regions)):
            with columns[i]:
                st.metric(r, f"£{v:,.0f}")
                st.caption(f"{p:.0%} of UK average")

    st.subheader("Volatility")
    returns = np.log(region_data[selected_regions]).diff()
    vol = returns.rolling(12).std()
    vol_fig = go.Figure()
    for r in vol.columns:
        vol_fig.add_trace(go.Scatter(x=vol.index, y=vol[r], name=r, mode="lines", hovertemplate="<b>%{fullData.name}</b>: %{y:,.4f}<extra></extra>",))
    vol_fig.update_layout(
        hovermode="x unified",
        dragmode="zoom",
        legend_title_text="Region",
        margin=dict(l=30, r=10, t=10, b=30),
        yaxis=dict(title="Rolling std of log returns"),
        xaxis=dict(title="Date", hoverformat="<b style='font-size: 0.8rem'>%Y<b>"),
    )
    st.plotly_chart(vol_fig, use_container_width=True)

with rebase_tab:
    st.header("Rebased prices")
    region_data = data.get_region_data(regions=tuple(selected_regions))

    if region_data.empty:
        st.info("No data available for the selected regions.")
    else:
        present, full_months, default_base = rebase.get_options(
            region_data, selected_regions)
        if not present:
            st.info("None of the selected regions are available in the dataset.")
        elif not full_months:
            st.warning("No month has data for all selected regions")
        else:
            col1, col2 = st.columns([3, 1])
            with col1:
                base_month = st.select_slider(
                    "Rebase month (base = 100)",
                    options=full_months,
                    value=default_base,
                    format_func=lambda d: d.strftime("%b %Y"),
                )
            with col2:
                show_before = st.checkbox("Show data before index month")

            fig = rebase.create_rebased_graph(
                region_data,
                present,
                base_month,
                include_before=show_before,
            )
            st.plotly_chart(fig, use_container_width=True,
                            theme="streamlit", config={"scrollZoom": False})

with corr_tab:
    region_data = data.get_region_data(regions=tuple(selected_regions), include_uk=False)

    returns = np.log(region_data[selected_regions]).diff()  # r_t = log P_t - log P_{t-1}
    corr = returns.corr()
    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.index,
        zmin=-1, zmax=1,
        hovertemplate="Corr: %{z:,.3f}<extra></extra>", 
    ))
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
