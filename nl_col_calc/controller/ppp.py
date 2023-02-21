import streamlit as st
# import numpy as np

from nl_col_calc.model import stmodels
# from nl_col_calc.utils.pandas_style import stylize
from nl_col_calc.utils.stutils import notify_text, calcresult


def ppp():
    st.header('Quick overview based on purchasing power parity index')
    notify_text('The purchashing power parity index ([PPP](https://en.wikipedia.org/wiki/Purchasing_power_parity)) allows for quick comparison of your standard of living in your current country and the Netherlands.')

    countries = stmodels.list_countries()
    countries = tuple((k, v) for k, v in sorted(countries.items(), key=lambda x: x[1]) if k != 'NLD')
    default_country_selected_index = tuple((k for k, v in countries)).index('USA')

    country_selected = st.selectbox(
        'What is your current country?', countries,
        index=default_country_selected_index, format_func=lambda x: x[1]
    )

    salary_original = st.number_input(
        f'What is your gross monthly salary converted to Euros (€) in {country_selected[1]}?',
        min_value=0, step=10, value=3000
    )

    salary_range = stmodels.calc_salary_range_from_ppp_for_country_and_salary(country_selected[0], salary_original)

    calcresult(f'Based on the PPP index you need a salary of €{salary_range[0]:.00f} to €{salary_range[1]:.00f} a month for a similar standard of living in the Netherlands.', ignore_add_sub=True)

    # st.dataframe(stylize(df))
    #st.line_chart(data=df)

    notify_text('Data from purchasing power parity index calculations are broad at best and might not apply well to your personal situation.')
