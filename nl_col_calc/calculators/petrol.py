import cbsodata
import re
import dateparser
import pandas as pd


# EU fuel type definitions
# https://ec.europa.eu/commission/presscorner/detail/en/IP_18_6101

eu_petrol_mappings = {
    'euro95': 'E10',
    'euro98': 'E5',
    'diesel': 'B7',
    'lpg': 'LPG',
}


def _to_eu_petrol_mappings(name):
    name = name.lower()
    for k, v in eu_petrol_mappings.items():
        if k in name:
            return v

        
def get_nld_petrol_prices():
    df = pd.DataFrame(cbsodata.get_data('80416NED'))

    # strip all rows that do not match a certain date pattern string
    df = df.loc[df.index[[bool(re.match('^[0-9]* [a-z]* [0-9]* [a-z]*$', x.lower().strip())) for x in df['Perioden']]]]

    # convert to datetime
    df['Perioden'] = pd.to_datetime(df['Perioden'].apply(lambda x: dateparser.parse(x, ['%Y %A %d %B'], languages=['nl'])))

    df.set_index('Perioden', inplace=True)
    df.index.rename('date', inplace=True)

    df.rename(columns={k: v for k, v in {x: _to_eu_petrol_mappings(x) for x in df.columns}.items() if v is not None}, inplace=True)

    df = df[[x for x in df.columns if x in eu_petrol_mappings.values()]]
    
    return df
