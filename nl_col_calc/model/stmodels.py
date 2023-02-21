import streamlit as st
import pycountry
import pandas as pd
import numpy as np

from nl_col_calc.calculators.purchasing_power import (
    get_all_ppp_scores_centered_to_country, center_all_ppp_scores_on_country
)


def calc_salary_range_from_ppp_for_country_and_salary(iso_a3_country, salary):
    dfs = _ppp_convert_latest_only(get_ppp_scores('NLD'))

    results = {}
    for name, df in dfs.items():
        if iso_a3_country not in df.index:
            # countries are not always available for all PPP indexes
            continue

        # st.write(name)
        # st.write(df.loc[iso_a3_country])

        # st.write(name)
        # st.write(df.loc[iso_a3_country])

        results[name] = (salary / df.loc[iso_a3_country])
        #st.write(df.loc[iso_a3_country].to_frame())

    # st.write(results)
    df = pd.DataFrame(results)
    df.index.rename('Year', inplace=True)
    df.sort_index(inplace=True)

    vals = df.values.flatten()
    vals = vals[~np.isnan(vals)]

    # st.write(vals)
    vals = _reject_outliers(vals)
    # st.write(vals)

    #salary_mi, salary_ma = np.min(vals), np.max(vals)
    salary_std = np.std(vals)
    salary_mean = np.median(vals)

    salary_range = np.clip(
        [salary_mean - salary_std * 1.96, salary_mean + salary_std * 1.96],
        a_min=0, a_max=None)

    return salary_range


def _reject_outliers(data, m=2.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    return data[s < m]


#@st.cache
def list_countries():
    dfs = get_ppp_scores('NLD')

    countries = set()
    for name, df in dfs.items():
        countries |= set(df.index.values)

    retval = {}
    for country in countries:
        cdata = pycountry.countries.get(alpha_3=country)

        if cdata is None:
            try:
                cdata = pycountry.countries.search_fuzzy(country)[0]
            except LookupError:
                cdata = None

        if cdata is not None:
            if hasattr(cdata, 'common_name'):
                retval[country] = cdata.common_name
            else:
                retval[country] = cdata.name.split(', ')[0]

    return retval

def _ppp_convert_latest_only(ppps):
    retvals = {}
    for k, v in ppps.items():
        # only keep the latest datapoint
        retvals[k] = v.T.sort_index().iloc[[-1]].T.dropna()

    return retvals


@st.cache_data
def get_ppp_scores(iso_a3_country):
    return get_all_ppp_scores_centered_to_country(iso_a3_country=iso_a3_country)
