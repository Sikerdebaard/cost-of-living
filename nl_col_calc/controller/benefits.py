# https://www.belastingdienst.nl/wps/wcm/connect/nl/toeslagen/content/hulpmiddel-proefberekening-toeslagen
import streamlit as st

from nl_col_calc.utils.stutils import notify_text, calcresult

name = 'Government benefits'


def benefits():
    st.header(name)

    notify_text('Government benefits change on a yearly basis and are influenced by policy makers.')

    notify_text('Please go to [this website](https://www.belastingdienst.nl/wps/wcm/connect/nl/toeslagen/content/hulpmiddel-proefberekening-toeslagen) to calculate your benefits. Choose the year that is closest to the year of your arrival. If you don\'t speak Dutch you can use [a translation tool](https://translate.google.com/) to assist you with the process.')

    st.write('What are the results of the calculator?')

    huurtoeslag = st.number_input('Huurtoeslag per month', min_value=0, value=0)
    kindgebonden_budget = st.number_input('Kindgebonden budget per month', min_value=0, value=0)
    kinderopvangtoeslag = st.number_input('Kinderopvangtoeslag per month', min_value=0, value=0)
    zorgtoeslag = st.number_input('Zorgtoeslag per month', min_value=0, value=0)

    result = {
        'huurtoeslag': huurtoeslag,
        'kindgebonden budget': kindgebonden_budget,
        'kinderopvangtoeslag': kinderopvangtoeslag,
        'zorgtoeslag': zorgtoeslag,
    }

    res = sum(result.values())

    calcresult(
            f'Based on your inputs you receive €{res:.00f} government benefits per month in the Netherlands.', add=[name, res] if res > 0 else None
    )
