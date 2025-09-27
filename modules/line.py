import plotly as pt


def create_line_graph(data, selected_regions):
    fig = pt.graph_objects.Figure()
    for region in data.columns:
        if region != "United Kingdom" or "United Kingdom" in selected_regions:
            fig.add_trace(
                pt.graph_objects.Scatter(
                    x=data.index,
                    y=data[region],
                    name=region,
                    mode="lines",
                    hovertemplate="<b>%{fullData.name}</b>: £%{y:,.0f}<extra></extra>",
                )
            )
    fig.update_layout(
        hovermode="x unified",
        dragmode="zoom",
        legend_title_text="Region",
        margin=dict(l=30, r=10, t=10, b=30),
        yaxis=dict(title="Average price (£)",
                   tickformat=",.2s", rangemode="tozero"),
        xaxis=dict(
            title="Date", hoverformat="<b style='font-size: 0.8rem'>%Y<b>"),
    )

    fig.update_xaxes(rangeslider_visible=False,
                     showspikes=True, spikemode="across", spikethickness=1)
    return fig


def perf_metrics(data, selected_regions):
    metrics = []
    uk_average = data["United Kingdom"].dropna().iloc[-1]
    for i, region in enumerate(selected_regions):
        value = data[region].dropna().iloc[-1]
        metrics.append([region, value, value/uk_average])
    return metrics
