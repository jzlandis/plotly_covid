import sys
sys.dont_write_bytecode = True

import dash
import dash_core_components as dcc
import dash_html_components as html

from figure import fig as us_covid_map


title = 'Covid-19 Data by US County'
exit()

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
    ]
)

if __name__ == '__main__':
    app.run_server()
