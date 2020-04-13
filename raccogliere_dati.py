from datetime import datetime
from urllib.request import urlopen
import json

date_format = "%Y-%m-%dT%H:%M:%S"

with urlopen(
    "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-province.json"
) as response:
    data = json.load(response)

time_series_data = {}
location2id = {}
for entry in data:
    date = datetime.strptime(entry["data"], date_format)
    cr = str(entry["codice_regione"])
    dr = entry["denominazione_regione"]
    cp = str(entry["codice_provincia"])
    dp = entry["denominazione_provincia"]
    sp = entry["sigla_provincia"]
    tc = entry["totale_casi"]
    if tc == 0:
        continue
    code = "italia" + cr + cp
    if code in time_series_data.keys():
        time_series_data[code][-1].append((date, (tc, None)))
    else:
        time_series_data[code] = [dp, dr, None, [(date, (tc, None)),]]
    location2id[", ".join((dp, dr))] = code
