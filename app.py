import sys

sys.dont_write_bytecode = True

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from data_gather import corona_dict, counties2fips
from map_figure import us_covid_map


title = "Covid-19 Data by US County"
location = 'Tarrant, Texas'

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = title

app.layout = html.Div([
    html.Div([
        html.H1(title),
    ], className='row'),
    html.Div([
        html.Div([
            dcc.Graph(
                id='us_covid_map',
                figure=us_covid_map,
                #style={'height': '100vh'}
            ),
        ], className='six columns'),
        html.Div([
            dcc.Graph(
                id='scatter',
                #style={'height': '30vh'}
            ),
            dcc.Dropdown(
                id='dropdown',
                options=[
                    {'label':k, 'value':v} for k, v in counties2fips.items()
                ],
                value=[counties2fips[location],],
                multi=True
            ),
            dcc.Checklist(
                id='log_selection',
                options=[
                    {'label': 'Y Log Scale', 'value': 'log'},
                    {'label': 'Cases Relative to Total', 'value': 'rel'}
                ],
                value=[]
            ),
        ], className='six columns')
    ], className='row'),
    html.Div([
        html.A("Code on Github", href="https://github.com/jzlandis/plotly_covid"),
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
            "County Population Data",
            href="https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv",
        ),
    ], className='row')
])

@app.callback(
    Output(component_id='scatter', component_property='figure'),
    [Input(component_id='dropdown', component_property='value'),
     Input(component_id='log_selection', component_property='value'),
    ]
)
def update_graph(county_values, plot_options):
    figure = go.Figure()
    for value in county_values:
        ys = [x[1][0] for x in corona_dict[value][3]]
        if 'rel' in plot_options:
            c = max(ys)*1.
        else:
            c = 1.
        figure.add_trace(go.Scatter(
            x=[x[0] for x in corona_dict[value][3]],
            y=[y/c for y in ys],
            name=', '.join(corona_dict[value][1::-1])
        ))
    ul_kwargs = {}
    title='Confirmed Cases vs. Date'
    xlabel='Date'
    ylabel='Confirmed Cases'
    if len(county_values) == 1:
        title += (' for ' + ', '.join(corona_dict[county_values[0]][1::-1]))
    if 'rel' in plot_options:
        title += ' (cases relative to total)'
        ylabel='Portion of Confirmed Cases'
    if 'log' in plot_options:
        ul_kwargs['yaxis_type'] = 'log'
        ylabel += ' (log scale)'
    figure.update_layout(
        title=title,
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        hovermode='x',
        **ul_kwargs
    )
    return figure


if __name__ == "__main__":
    app.run_server()
