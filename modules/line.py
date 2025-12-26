import plotly as pt
import pandas as pd
import streamlit as st



@st.cache_data
def create_line(data, region_names):
    fig = pt.graph_objects.Figure()
    for region, label in zip(data.index, region_names):
        fig.add_trace(
            pt.graph_objects.Scatter(
                x=data.columns,
                y=data.loc[region],
                name=label,
                mode="lines",
                hovertemplate="<b>%{fullData.name}</b>: £%{y:,.0f}<extra></extra>"))
    fig.update_layout(
        hovermode="x unified",
        dragmode="zoom",
        legend_title_text="Region",
        margin=dict(l=30, r=10, t=10, b=30),
        yaxis=dict(title="Average price (£)", tickformat=",.2s", rangemode="tozero"),
        xaxis=dict(title="Date", hoverformat="<b>%Y<b>"))

    fig.update_xaxes(rangeslider_visible=False,
                     showspikes=True, spikemode="across", spikethickness=1)
    return fig