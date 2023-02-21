import streamlit as st
import pandas as pd

from nl_col_calc.calculators.energy import get_energy_prices

from nl_col_calc.utils.stutils import notify_text, calcresult


name = 'Insurances'

def gen_insured_name(insured, insured_mappings):
    if isinstance(insured, list):
        return 'houses (both as an owner or when renting)'

    if insured in (3, 4):
        return 'houses (only applies for owners)' if insured == 3 else 'houses (only applies for rental units)'

    if insured_mappings[insured] is None:
        return ''

    return f'{insured_mappings[insured]}s'

def insurance():
    st.header('Insurances')

    notify_text('In the Netherlands you are required by law to have a health insurance at a minimum, and a WA insurance if you own a motor vehicle. This tool is not exhaustive in all the things that can be insured but instead focusses on the most common insurances. You can use tools like [pricewise](https://www.pricewise.nl/zorgverzekering) and [independer](https://www.independer.nl/zorgverzekering/) to compare insurances. Fill in 0 for insurances that do not apply.')

    insured = {
            1: 'person',
            2: 'motor verhicle',
            3: 'house (owner)',
            4: 'house (rental)',
            5: None,
    }

    insurances = {
            'health insurance (zorgverzekering)': (1, 150),
            'motor vehicle (WA-verzekering)': (2, 50),
            'liability (aansprakelijkheidsverzekering)': (1, 7.5),
            'contents insurance (inboedelverzekering)': ([3, 4], 7.5),
            'building insurance (opstalverzekering)': (3, 15),
            'travel insurance (reisverzekering)': (1, 10),
            'legal expenses insurance (rechtsbijstandverzekering)': (1, 25),
            'other insurances': (5, 0),
    }

    results = {}
    for k, v in insurances.items():
        results[k] = st.number_input(f'Monthly premium for {k} all {gen_insured_name(v[0], insured)} combined?', min_value=0., value=float(v[1]))

    res = sum(results.values())

    calcresult(f'Estimated total monthly insurance premiums: €{res:.02f}.', sub=[name, res] if res > 0 else None)
