from nl_col_calc.utils.requests import pandas_get 
import pandas as pd
import statsmodels.api as sm

from zipfile import ZipFile
from io import BytesIO
from datetime import datetime


def get_worldbank_pa_nus_ppp(years_ago):
    # GDP based purchasing power - not really relevant on an individual basis but more on a country level
    url = 'https://api.worldbank.org/v2/en/indicator/PA.NUS.PPP?downloadformat=csv'
    req = pandas_get(url)

    #zipfile = ZipFile(BytesIO(req.content))
    zipfile = ZipFile(req)

    valid_files = [x for x in zipfile.namelist() if x.upper().startswith('API_PA.NUS')]
    assert len(valid_files) == 1


    with zipfile.open(valid_files[0], 'r') as csvfile:
        skiprows = 0
        last_updated = None
        for line in csvfile.readlines():
            # we are interested in this metadata field
            if b'last updated' in line.lower().strip():
                last_updated = line.strip().split(b',')[1].decode().strip('""')

            # figure out where the csv file actually starts since worldbank adds metadata at the top
            if b'country name' in line.lower().strip():
                break

            skiprows += 1
            
    with zipfile.open(valid_files[0], 'r') as csvfile:
        df = pd.read_csv(csvfile, skiprows=skiprows, index_col='Country Code')
    
    # we are only interested in PPP values over the last x years
    no_older_than = datetime.now().year - years_ago
    df = df[[x for x in df.columns if x.isnumeric() and int(x) >= no_older_than]].copy()

    # drop all countries with only NaN values
    df.dropna(axis=0, how='all', inplace=True)
    
    # center around 0 (USA is always 1 in this dataset)
    # to make it more comparable to BigMac Index
    #df = df - 1

    # sort all axis
    df = df[sorted(df.columns, reverse=True, key=lambda x: int(x))]
    df.sort_index(inplace=True)

    # normalize some data
    df.index.rename('country', inplace=True)
    df.rename(columns={x: str(x) for x in df.columns}, inplace=True)

    return df


def _bigmac_fit_predict(df):
    # adj_price=lm(dollar_price ~ GDP_bigmac) %>% predict
    
    x = df[['GDP_bigmac']]
    y = df['dollar_price']

    x = sm.add_constant(x) # adding a constant

    model = sm.OLS(y, x).fit()
    
    pred = model.get_prediction(x)

    return pred.summary_frame(alpha=0.05).sort_values('mean')


def get_bigmac_index_ppp(years_ago):
    # method from https://github.com/TheEconomist/big-mac-data/blob/master/Big%20Mac%20data%20generator.ipynb
    # translated to Python
    
    df = pd.read_csv(pandas_get('https://raw.githubusercontent.com/TheEconomist/big-mac-data/master/source-data/big-mac-source-data-v2.csv'))

    df['date'] = pd.to_datetime(df['date'])
    df['dollar_price'] = df['local_price'] / df['dollar_ex']

    base_currency = 'USD'
    base_currencies = [base_currency]
    
    for date in df['date'].unique():
        idx = df.index[df['date'] == date]
        sel = df.loc[idx]
        for currency in base_currencies:
            df.loc[idx, f'big_mac_index_{currency}'] = sel['dollar_price'] / sel[sel['currency_code'] == currency]['dollar_price'].mean() - 1
    
    # pivot table
    df = pd.pivot(df, index='iso_a3', columns='date', values=f'big_mac_index_{base_currency}')
    df.columns = pd.to_datetime(df.columns)
    
    
    # resample and take only the latest datapoint for every year
    df = df[df.columns.sort_values()].T.groupby(df.columns.year).last().T

    # we are only interested in PPP values over the last 4 years
    no_older_than = datetime.now().year - years_ago
    df = df[[x for x in df.columns if int(x) >= no_older_than]].copy()

    # drop all countries with only NaN values
    df.dropna(axis=0, how='all', inplace=True)

    # sort all axis
    df = df[sorted(df.columns, reverse=True, key=lambda x: int(x))]
    df.sort_index(inplace=True)

    # normalize some data
    df.index.rename('country', inplace=True)
    df.rename(columns={x: str(x) for x in df.columns}, inplace=True)
        
    return df


def get_adjusted_bigmac_index_ppp(years_ago):
    # method from https://github.com/TheEconomist/big-mac-data/blob/master/Big%20Mac%20data%20generator.ipynb
    # translated to Python
    
    df = pd.read_csv(pandas_get('https://raw.githubusercontent.com/TheEconomist/big-mac-data/master/source-data/big-mac-source-data-v2.csv'))

    df['date'] = pd.to_datetime(df['date'])
    df = df[df['GDP_local'] > 0].copy()
    df['dollar_price'] = df['local_price'] / df['dollar_ex']

    for date in df['date'].unique():
        idx = df.index[df['date'] == date]
        usa_price = df[(df['date'] == date) & (df['iso_a3'] == 'USA')]['local_price'].mean()
        df.loc[idx, 'GDP_bigmac'] = df['GDP_local'] / (df['local_price'] / usa_price)
        
    df_linreg = pd.DataFrame()
    for date in df['date'].unique():
        sel = df[df['date'] == date]
        pred = _bigmac_fit_predict(sel.copy())

        df_linreg = pd.concat([df_linreg, pred])

    df_linreg.sort_index(inplace=True)
    df_linreg = df_linreg.add_prefix('adjusted_price_')
    
    df = df.join(df_linreg)

    base_currency = 'USD'
    base_currencies = [base_currency]
    
    for date in df['date'].unique():
        idx = df.index[df['date'] == date]
        sel = df.loc[idx]
        for currency in base_currencies:
            df.loc[idx, f'big_mac_index_{currency}'] = (sel['dollar_price'] / sel['adjusted_price_mean']) / \
                (sel[sel['currency_code'] == currency]['dollar_price'].mean() / sel[sel['currency_code'] == currency]['adjusted_price_mean'].mean()) - 1
    
    # pivot table
    df = pd.pivot(df, index='iso_a3', columns='date', values=f'big_mac_index_{base_currency}')
    df.columns = pd.to_datetime(df.columns)
    
    
    # resample and take only the latest datapoint for every year
    df = df[df.columns.sort_values()].T.groupby(df.columns.year).last().T

    # we are only interested in PPP values over the last 4 years
    no_older_than = datetime.now().year - years_ago
    df = df[[x for x in df.columns if int(x) >= no_older_than]].copy()

    # drop all countries with only NaN values
    df.dropna(axis=0, how='all', inplace=True)

    # sort all axis
    df = df[sorted(df.columns, reverse=True, key=lambda x: int(x))]
    df.sort_index(inplace=True)

    # normalize some data
    df.index.rename('country', inplace=True)
    df.rename(columns={x: str(x) for x in df.columns}, inplace=True)
    
    return df


def get_oecd_price_levels_ppp():
    url = 'https://stats.oecd.org/SDMX-JSON/data/CPL?contentType=csv'

    df = pd.read_csv(pandas_get(url))

    df['date'] = pd.to_datetime(df['TIME']).dt.year
    df = df[df['Country currency'].str.contains('USD')]

    df = df.groupby(['LOCATION']).last()[['date', 'Value']].reset_index().pivot_table(index='LOCATION', columns='date',
                                                                                      values='Value')

    df = df / 100

    # drop all countries with only NaN values
    df.dropna(axis=0, how='all', inplace=True)

    # sort all axis
    df = df[sorted(df.columns, reverse=True, key=lambda x: int(x))]
    df.sort_index(inplace=True)

    # normalize some data
    df.index.rename('country', inplace=True)
    df.rename(columns={x: str(x) for x in df.columns}, inplace=True)

    return df


def center_on_country(df, idx_country):
    if idx_country not in df.index:
        return None

    return (df + (1 - df.loc[idx_country]))


def _reject_negative_vals(df):
    df[df < 0] = float('nan')

    return df


def center_all_ppp_scores_on_country(ppps, iso_a3_country):
    retvals = {k: center_on_country(v, iso_a3_country) for k, v in ppps.items()}

    return {k: v for k, v in retvals.items() if v is not None}


def get_all_ppp_scores_centered_to_country(iso_a3_country, years_ago=2):
    retvals = {
        #'World Bank PA.NUS.PPP': get_worldbank_pa_nus_ppp(years_ago),
        'OECD Monthly comparative price levels PPP': get_oecd_price_levels_ppp(),
        'Adjusted BigMac Index PPP': get_adjusted_bigmac_index_ppp(years_ago),
        'BigMac Index PPP': get_bigmac_index_ppp(years_ago),
    }

    retvals = center_all_ppp_scores_on_country(retvals, iso_a3_country)

    return {k: v for k, v in retvals.items() if v is not None}
