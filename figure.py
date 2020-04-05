import math
import json
from urllib.request import urlopen
from datetime import datetime

import pandas as pd
import plotly.express as px


with urlopen(
    "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
) as response:
    counties = json.load(response)


nyc_fips = ("36047", "36081", "36085", "36061", "36005")
nyc_counties = ("Kings", "Queens", "Richmond", "New York", "Bronx")
nyt_counties = (
    "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv"
)


def nozerodiverror(numerator, denomenator):
    if denomenator == 0:
        return 0.0
    else:
        return numerator / denomenator


def nozeroerrorlog(x):
    if x == 0:
        return 0
    else:
        return math.log(x)


pops_csv = pd.read_csv("co_est2019.csv", dtype={"STATECOUNTY": str})
fips2pops = {v[0]: v[1] for v in pops_csv.values}
fips = set(pops_csv["STATECOUNTY"])
nyc_total_pop = sum(fips2pops[fip] for fip in nyc_fips)
for fip in nyc_fips:
    fips2pops[fip] = nyc_total_pop


corona_csv = pd.read_csv(nyt_counties, dtype={"fips": str, "cases": int, "deaths": int})

# check all fips codes in NYT data is in pop data
nyt_fips = set(x for x in corona_csv["fips"] if type(x) is str)
assert nyt_fips.issubset(fips)

parse_time = lambda x: datetime.strptime(x, "%Y-%m-%d")

corona_dict = {}
nyc_fips_codes_seen = set()
fips_codes_seen = set()
for date, county, state, fips_code, cases, deaths in corona_csv.values:
    if (county, state) == ("New York City", "New York"):
        for fips_code, county in zip(nyc_fips, nyc_counties):
            if not fips_code in nyc_fips_codes_seen:
                corona_dict[fips_code] = [
                    "New York",
                    county,
                    fips2pops[fips_code],
                    [(parse_time(date), (cases, deaths))],
                ]
                nyc_fips_codes_seen.add(fips_code)
            else:
                corona_dict[fips_code][-1].append((parse_time(date), (cases, deaths)))
    elif type(fips_code) == str and any(x != 0 for x in (cases, deaths)):
        if not fips_code in fips_codes_seen:
            corona_dict[fips_code] = [
                state,
                county,
                fips2pops[fips_code],
                [(parse_time(date), (cases, deaths))],
            ]
            fips_codes_seen.add(fips_code)
        else:
            corona_dict[fips_code][-1].append((parse_time(date), (cases, deaths)))

fips_array = []
cases_array = []
deaths_array = []
population = []
cases_per_capita = []
deaths_per_capita = []
deaths_per_case = []
county_state = []
first_dates = []
last_dates = []
for fips_code, (state, county, pop, case_death_data) in corona_dict.items():
    fips_array.append(fips_code)
    cases_array.append(case_death_data[-1][1][0])
    deaths_array.append(case_death_data[-1][1][1])
    population.append(pop)
    first_dates.append(case_death_data[0][0].strftime("%b %d"))
    last_dates.append(case_death_data[-1][0].strftime("%b %d"))
    cases, deaths = case_death_data[-1][1]
    cases_per_capita.append(f"{round(cases*100000/pop, 1):.1f}")
    deaths_per_capita.append(f"{round(deaths*100000/pop, 1):.1f}")
    deaths_per_case.append(f"{round(nozerodiverror(deaths, cases), 3):.3f}")
    county_state.append(", ".join([county, state]))

corona_df = pd.DataFrame.from_dict(
    {
        "fips": fips_array,
        "Total Cases": cases_array,
        "Total Deaths": deaths_array,
        "Population": population,
        "Cases per 100,000 Population": cases_per_capita,
        "Deaths per 100,000 Population": deaths_per_capita,
        "Deaths per Case": deaths_per_case,
        "Location": county_state,
        "Date of First Recorded Case": first_dates,
        "Date of Most Recent Data Update": last_dates,
    }
)

color_weights = [
    nozeroerrorlog(float(x)) for x in corona_df["Cases per 100,000 Population"]
]

# mapper = px.choropleth
mapper = px.choropleth_mapbox

mapper_kwargs = {
    px.choropleth: {"scope": "usa",},
    px.choropleth_mapbox: {
        "mapbox_style": "carto-positron",
        "zoom": 3,
        "center": {"lat": 37.0902, "lon": -95.7129},
        "opacity": 0.5,
    },
}

fig = mapper(
    corona_df,
    geojson=counties,
    locations="fips",
    color=color_weights,
    color_continuous_scale="Viridis",
    range_color=(0, max(color_weights)),
    labels={"color": "Log(Cases/100000)", "fips": "County FIPS Code"},
    hover_data=[
        "Location",
        "Total Cases",
        "Date of First Recorded Case",
        "Date of Most Recent Data Update",
        "Total Deaths",
        "Population",
        "Cases per 100,000 Population",
        "Deaths per 100,000 Population",
        "Deaths per Case",
    ],
    **mapper_kwargs[mapper],
)

fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

if __name__ == "__main__":
    fig.show()
