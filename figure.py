import sys
import math

from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

import pandas as pd

pops_csv = pd.read_csv('co_est2019.csv', dtype={'STATECOUNTY':str})
fips2pops = {v[0]: v[1] for v in pops_csv.values}
fips = set(pops_csv['STATECOUNTY'])

nyt_counties = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'

corona_csv = pd.read_csv(nyt_counties, dtype={'fips':str, 'cases':int, 'deaths':int})

# check all fips codes in NYT data is in pop data
nyt_fips = set(x for x in corona_csv['fips'] if type(x) is str)
assert nyt_fips.issubset(fips)

corona_dict = {fips_code: (cases, deaths, fips2pops[fips_code], state, county)
                   for fips_code, cases, deaths, state, county
                       in zip(corona_csv['fips'], corona_csv['cases'], corona_csv['deaths'],
                              corona_csv['state'], corona_csv['county'])
                       if type(fips_code) == str
              }

fips_array        = []
cases_array       = []
deaths_array      = []
population        = []
cases_per_capita  = []
deaths_per_capita = []
deaths_per_case   = []
county_state      = []
for fips_code, (cases, deaths, pop, state, county) in corona_dict.items():
    fips_array.append(fips_code)
    cases_array.append(cases)
    deaths_array.append(deaths)
    population.append(pop)
    cases_per_capita.append(f"{round(cases*100000/pop, 1):.1f}")
    deaths_per_capita.append(f"{round(deaths*100000/pop, 1):.1f}")
    deaths_per_case.append(f"{round(deaths/cases, 3):.3f}")
    county_state.append(', '.join([county, state]))

corona_df = pd.DataFrame.from_dict({'fips'                          : fips_array,
                                    'Total Cases'                   : cases_array,
                                    'Total Deaths'                  : deaths_array,
                                    'Population'                    : population,
                                    'Cases per 100,000 Population'  : cases_per_capita,
                                    'Deaths per 100,000 Population' : deaths_per_capita,
                                    'Deaths per Case'               : deaths_per_case,
                                    'Location'                      : county_state,
                                    })

import plotly.express as px

color_weights = [math.log(float(x)) for x in corona_df['Cases per 100,000 Population']]

#mapper = px.choropleth
mapper = px.choropleth_mapbox

mapper_kwargs = {px.choropleth: {'scope': 'usa',},
                 px.choropleth_mapbox: {'mapbox_style': 'carto-positron', 'zoom': 4,
                                        'center' : {'lat': 37.0902, 'lon': -95.7129},
                                        'opacity': 0.5}
                }

fig = mapper(corona_df, geojson=counties,
                        locations='fips',
                        color=color_weights,
                        color_continuous_scale='Viridis',
                        range_color=(0, max(color_weights)),
                        hover_data = ['Location', 'Total Cases',
                                      'Total Deaths', 'Population',
                                      'Cases per 100,000 Population',
                                      'Deaths per 100,000 Population',
                                      'Deaths per Case'],
                        **mapper_kwargs[mapper])

fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

if __name__ == '__main__':
    fig.show()
