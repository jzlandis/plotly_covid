import sys

sys.dont_write_bytecode = True

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from data_gather import corona_dict, counties2fips
from map_figure import us_covid_map

from raccogliere_dati import time_series_data as italian_data
from raccogliere_dati import location2id as ita_loc2id

corona_dict = {**corona_dict, **italian_data}
counties2fips = {**counties2fips, **ita_loc2id}

title = "Covid-19 Data for Select Regions"
location = "Tarrant, Texas"

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = title

app.layout = html.Div(
    [
        html.Div([html.H1(title),], className="row"),
        html.Div(
            [
                html.Div(
                    [
                        html.H3("Cases per US County - colored by log(cases/100k ppl)"),
                        dcc.Graph(id="us_covid_map", figure=us_covid_map,),
                    ],
                    className="six columns",
                ),
                html.Div(
                    [
                        html.H3("Confirmed Cases vs. Date"),
                        dcc.Graph(id="scatter",),
                        html.P(
                            f"Select Regional Data to Plot "
                            f"(US Counties + Italian Provinces)"
                        ),
                        dcc.Dropdown(
                            id="dropdown",
                            options=[
                                {"label": k, "value": v}
                                for k, v in counties2fips.items()
                            ],
                            value=[counties2fips[location],],
                            multi=True,
                        ),
                        dcc.Checklist(
                            id="log_selection",
                            options=[{"label": "Y Log Scale", "value": "log"},],
                            value=[],
                        ),
                        dcc.RadioItems(
                            id="case_display_mode",
                            options=[
                                {"label": "Raw Case Numbers (default)", "value": "raw"},
                                {"label": "Cases Relative to Peak", "value": "reltot"},
                                {
                                    "label": "Cases Relative to Population",
                                    "value": "relpop",
                                },
                            ],
                            value="raw",
                            labelStyle={"display": "inline-block"},
                        ),
                        dcc.RadioItems(
                            id="counts_type",
                            options=[
                                {
                                    "label": "Cumulative Total Cases (default)",
                                    "value": "cum",
                                },
                                {"label": "Delta Cases per Day", "value": "delta"},
                            ],
                            value="cum",
                            labelStyle={"display": "inline-block"},
                        ),
                    ],
                    className="six columns",
                ),
            ],
            className="row",
        ),
        html.Div(
            [
                html.A(
                    "Code on Github", href="https://github.com/jzlandis/plotly_covid"
                ),
                html.Br(),
                html.A(
                    "New York Times Covid-19 Data",
                    href="https://github.com/nytimes/covid-19-data",
                ),
                html.Br(),
                html.P(
                    "Counties in the New York City area report total cases for all of Bronx, Kings, New York, Queens, and Richmond counties on each county and compare them to the sum of all 5 counties populations"
                ),
                html.A(
                    "New York Times Covid-19 US Case Data Maps",
                    href="https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html",
                ),
                html.Br(),
                html.A(
                    "US County Population Data",
                    href="https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv",
                ),
                html.Br(),
                html.A(
                    "Dipartimento della Protezione Civile Italian Case Data",
                    href="https://github.com/pcm-dpc/COVID-19",
                ),
                html.Br(),
                html.A(
                    "Italian province populations",
                    href="https://www.comuniecitta.it/province-italiane-per-popolazione",
                ),
            ],
            className="row",
        ),
    ]
)


@app.callback(
    Output(component_id="scatter", component_property="figure"),
    [
        Input(component_id="dropdown", component_property="value"),
        Input(component_id="log_selection", component_property="value"),
        Input(component_id="case_display_mode", component_property="value"),
        Input(component_id="counts_type", component_property="value"),
    ],
)
def update_graph(county_values, plot_options, case_display_mode, counts_type):
    figure = go.Figure()
    for value in county_values:
        if counts_type == "cum":
            ys = [x[1][0] for x in corona_dict[value][3]]
        elif counts_type == "delta":
            ybase = corona_dict[value][3]
            ys = [ybase[0][1][0],] + [
                ybase[i + 1][1][0] - ybase[i][1][0] for i in range(len(ybase) - 1)
            ]
        if case_display_mode == "reltot":
            c = max(ys) * 1.0
        elif case_display_mode == "relpop":
            c = corona_dict[value][2] / 100000.0
        else:
            c = 1.0
        figure.add_trace(
            go.Scatter(
                x=[x[0] for x in corona_dict[value][3]],
                y=[y / c for y in ys],
                name=", ".join(corona_dict[value][1::-1]),
            )
        )
    ul_kwargs = {}
    if counts_type == "cum":
        title = "Cumulative Confirmed Cases vs. Date"
        ident = "Cumulative Cases"
    elif counts_type == "delta":
        title = "Delta Confirmed Cases vs. Date"
        ident = "Delta Cases"
    xlabel = "Date"
    ylabel = ident
    if len(county_values) == 1:
        title += " for " + ", ".join(corona_dict[county_values[0]][1::-1])
    if case_display_mode == "reltot":
        title += f" ({ident.lower()} relative to peak)"
        ylabel = f"Portion of {ident.lower()}"
    elif case_display_mode == "relpop":
        title += f" ({ident.lower()} relative to population)"
        ylabel = f"{ident} / 100k People"
    if "log" in plot_options:
        ul_kwargs["yaxis_type"] = "log"
        ylabel += " (log scale)"
    figure.update_layout(
        title=title, xaxis_title=xlabel, yaxis_title=ylabel, hovermode="x", **ul_kwargs
    )
    return figure


if __name__ == "__main__":
    app.run_server()
