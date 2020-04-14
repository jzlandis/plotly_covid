from datetime import datetime
from urllib.request import urlopen
import json
import pandas as pd

date_format = "%Y-%m-%dT%H:%M:%S"

population_file = "popolazione_italiane_province.csv"
pops_csv = pd.read_csv(
    population_file, dtype={'Poplazione': str},
    encoding='ISO-8859-1'
)
provreg2pop = {
    ', '.join(v[::2]): int(v[1].replace('.', '')) for v in pops_csv.values
}
provreg2pop['Sud Sardegna, Sardegna'] = (
    provreg2pop['Carbonia Iglesias, Sardegna']
    + provreg2pop['Medio Campidano, Sardegna']
)



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
    if tc == 0 or dp == 'In fase di definizione/aggiornamento':
        continue
    code = "italia" + cr + cp
    provreg = ", ".join((dp, dr))
    if code in time_series_data.keys():
        time_series_data[code][-1].append((date, (tc, None)))
    else:
        time_series_data[code] = [dp, dr, provreg2pop[provreg], [(date, (tc, None)),]]
    location2id[provreg] = code
