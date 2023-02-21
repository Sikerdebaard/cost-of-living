import streamlit as st
import pandas as pd

from nl_col_calc.calculators.energy import get_energy_prices

from nl_col_calc.utils.stutils import notify_text, calcresult


name = 'Water'


def water():
    st.header(name)

    notify_text('The tapwater in the Netherlands is [one of the cleanest in the world](https://epi.yale.edu/epi-results/2020/component/h2o) and it is one of our national prides. The tapwater is potable eliminating the need to buy bottled water. This has the added benefit of reducing plastic waste. Tapwater in the Netherlands is used for laundry, toilet, shower, cooking etc. Default tariffs are extracted from [NIBUD](https://www.nibud.nl/onderwerpen/uitgaven/kosten-energie-water/#Watergebruik).')

    tariffs = {
        1:	(68, 13.50),
        2:	(95, 16.50),
        3:	(123, 19.50),
        4:	(163, 24),
        5:	(187, 26.50),
    }
    
    num_people = st.radio('Number of people', tariffs.keys())

    results = {
        'm³ water': tariffs[num_people][0],
        'water': tariffs[num_people][1],
    }

    calcresult(
            f'Based on your inputs the cost of water is approximately €{results["water"]:.00f} per month in the Netherlands.', sub=[name, results['water']] if results['water'] > 0 else None
    )

