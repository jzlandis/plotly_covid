from datetime import timedelta
from datetime import datetime
import pandas as pd
import urllib

date_format = '%Y%m%d'
def date0():
    return datetime.strptime('20200224', date_format)
base_dati_province = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-%s.csv'

date_check = date0()
day = timedelta(days=1)

data = {}
dates = []

while True:
    try:
        csv_url = base_dati_province % date_check.strftime(date_format)
        #print('working on', csv_url)
        data[date_check] = pd.read_csv(
            csv_url,
            dtype={
                'totale_casi': int,
                'codice_regione': str,
                'codice_provincia': str}
        )
        dates.append(date_check)
    except urllib.error.HTTPError:
        break
    date_check += day

date_check = date0()

time_series_data = {}
location2id = {}
for date, data in data.items():
    for cr, dr, cp, dp, sp, tc in zip(
        data['codice_regione'],
        data['denominazione_regione'],
        data['codice_provincia'],
        data['denominazione_provincia'],
        data['sigla_provincia'],
        data['totale_casi']
    ):
        if tc == 0:
            continue
        code = 'italia' + cr + cp
        if code in time_series_data.keys():
            time_series_data[code][-1].append((date, (tc, None)))
        else:
            time_series_data[code] = [dp, dr, None, [(date, (tc, None)),]]
        location2id[', '.join((dp, dr))] = code
