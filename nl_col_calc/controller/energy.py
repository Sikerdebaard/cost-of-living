import streamlit as st
import pandas as pd

from nl_col_calc.calculators.energy import get_energy_prices

from nl_col_calc.utils.stutils import notify_text, calcresult


name = 'Energy cost (gas / electric)'


@st.cache_data(ttl=86400)  # cache for ~1 day
def _get_energy_prices():
    get_for_last_x_days = 12 * 3 * 30  # how much data do we retrieve?

    today = pd.to_datetime('today').normalize().date()
    past = (today - pd.Timedelta(days=get_for_last_x_days))

    return get_energy_prices(past, today).sort_index()


def energy():
    st.header(name)

    notify_text('You can compare various energy contracts using tools like [pricewise](https://www.pricewise.nl/energie-vergelijken/) and [independer](https://www.independer.nl/energie/). This calculator only approximates the contract costs. Default tariffs by [energy zero](https://www.energyzero.nl/energiecontract/stroom-en-gas/flextarieven).')

    df_prices = _get_energy_prices()
    df_prices = df_prices.iloc[-1:]

    kwh_price = st.number_input('Tariff €/kWh', min_value=.0, value=df_prices.iloc[0]['kWh_electricity_max'])
    kwh = st.number_input(f'How many kWh of electricity do you expect to use per year?', min_value=0, value=2500)

    m3_price = st.number_input('Tariff €/m³', min_value=.0, value=df_prices.iloc[0]['m3_natural_gas_max'])
    m3 = st.number_input(f'How many m³ of gas do you expect to use per year?', min_value=0, value=1200)

    leveringskosten_per_jaar = 150

    results = {
        'kWh': kwh * kwh_price / 12 * 1.21 + leveringskosten_per_jaar / 12 / 2,
        'm3': m3 * m3_price / 12 * 1.21 + leveringskosten_per_jaar / 12 / 2,
    }

    res = sum(results.values())

    calcresult(
            f'Based on your inputs the energy cost are approximately €{res:.00f} per month in the Netherlands.', sub=[name, res] if res > 0 else None
    )

