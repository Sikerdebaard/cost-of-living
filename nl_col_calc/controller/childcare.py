# https://www.belastingdienst.nl/wps/wcm/connect/nl/toeslagen/content/hulpmiddel-proefberekening-toeslagen
import streamlit as st

from nl_col_calc.utils.stutils import notify_text, calcresult

import pandas as pd

name = 'Childcare'


def childcare():
    st.header(name)

    st.markdown('Cost of childcare benefits. E.g. after school care. The numbers suggested here are based on the maximum tariffs published by the government https://www.rijksoverheid.nl/onderwerpen/kinderopvangtoeslag/bedragen-kinderopvangtoeslag-2023')
    notify_text('daycares are allowed to ask more than the maximum tariffs and those will have to be paid out of pocket.<br><bold style="color: red;">DO NOT BLINDLY FOLLOW THE RATES DESCRIBED HERE</bold>: check the daycare rates before signing any contracts.')

    tariffs = {
        'Dagopvang (daycare)': 9.12,
        'Buitenschoolseopvang (after-school care)': 7.85,
        'Gastouderopvang (host parent care)': 6.85,
    }

    st.write(pd.DataFrame.from_dict({k: f'€{v:0.2f} / hour' for k, v in tariffs.items()}, orient='index', columns=['Tariffs 2023']))

    result = {}
    for k, v in tariffs.items(): 
        result[k] = st.number_input(f'How many hours of {k} do you need per week in total?', min_value=0, value=0) * tariffs[k] * 52 / 12

    res = sum(result.values())

    calcresult(
            f'Based on your inputs the minimum cost of daycare is €{res:.00f} per month in the Netherlands.', sub=[name, res] if res > 0 else None
    )

