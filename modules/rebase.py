import pandas as pd
import plotly as pt


def get_options(region_data, selected_regions, preferred=pd.Timestamp("2008-01-01")):
    present = [r for r in selected_regions if r in region_data.columns]
    if not present:
        return [], [], None
    coverage_mask = region_data[present].notna().all(axis=1)
    full_months = list(region_data.index[coverage_mask])
    if not full_months:
        return present, [], None

    after = [d for d in full_months if d >= preferred]
    default_base = after[0] if after else full_months[-1]
    return present, full_months, default_base


def create_rebased_graph(region_data, regions, base_month, include_before=False):
    if not regions or base_month is None:
        return pt.graph_objects.Figure()

    plot_data = region_data.loc[:, regions].copy()
    if not include_before:
        plot_data = plot_data.loc[plot_data.index >= base_month]

    base_vals = region_data.loc[base_month, regions]
    indexed = plot_data.divide(base_vals).multiply(100.0)

    fig = pt.graph_objects.Figure()
    for region in indexed.columns:
        fig.add_trace(
            pt.graph_objects.Scatter(
                x=indexed.index,
                y=indexed[region],
                name=region,
                mode="lines",
                hovertemplate="<b>%{fullData.name}</b>: %{y:.1f}<extra></extra>",
            )
        )
    fig.update_layout(
        hovermode="x unified",
        dragmode="zoom",
        legend_title_text="Region",
        margin=dict(l=30, r=10, t=10, b=30),
        yaxis=dict(title="Index (base month = 100)", rangemode="tozero"),
        xaxis=dict(title="Month"),
    )
    fig.update_xaxes(
        rangeslider_visible=False,
        showspikes=True,
        spikemode="across",
        spikethickness=1,
    )
    return fig
