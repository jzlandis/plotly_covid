import sys
sys.dont_write_bytecode = True

import dash
import dash_core_components as dcc
import dash_html_components as html

from figure import fig as us_covid_map


title = 'Covid-19 Data by US County'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=title

app.layout = html.Div(children=[
    html.H1(title),
    dcc.Graph(
        id='us_covid_map',
        figure=us_covid_map
    ),
    html.A('Code on Github', href='https://github.com/jzlandis/plotly_covid'),
    html.Br(),
    html.A('New York Times Covid-19 Data', href='https://github.com/nytimes/covid-19-data'),
    html.Br(),
    html.P('Counties in the New York City area report total cases for all of Bronx, Kings, New York, Queens, and Richmond counties on each county and compare them to the sum of all 5 counties populations'),
    html.Br(),
    html.A('County Population Data', href='https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv')
    ]
)

if __name__ == '__main__':
    app.run_server()
