import plotly.express as px

from data_gather import corona_df, nozerodiverror, nozeroerrorlog, counties


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

us_covid_map = mapper(
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

us_covid_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

if __name__ == "__main__":
    us_covid_map.show()
