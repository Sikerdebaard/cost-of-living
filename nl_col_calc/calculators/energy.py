import matplotlib.pyplot as plt
import pandas as pd

from nl_col_calc.utils.requests import req_get


def get_energy_prices(from_date, to_date, resample='M'):
    base_url = f'https://api.energyzero.nl/v1/energyprices?fromDate={from_date}T22%3A00%3A00.000Z&tillDate={to_date}T23%3A59%3A59.999Z&interval=4'
    
    electricity_url = f'{base_url}&usageType=1&inclBtw=true'
    natgas_url = f'{base_url}&usageType=3&inclBtw=true'
    
    electr = req_get(electricity_url).json()
    natgas = req_get(natgas_url).json()
    
    df_res = None
    
    for k, v in zip(['kWh_electricity', 'm3_natural_gas'], [electr, natgas]):
        df = pd.DataFrame(v['Prices'])
        df['readingDate'] = pd.to_datetime(df['readingDate'])
        df.set_index('readingDate', inplace=True)
        df.index.rename('date', inplace=True)
        df.rename(columns={'price': k}, inplace=True)
        df = df[k].resample(resample).agg(['mean', 'median', 'std', 'min', 'max']).add_prefix(f'{k}_')
        
        if df_res is None:
            df_res = df
        else:
            df_res = df_res.join(df, how='outer')

    return df_res
