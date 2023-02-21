import streamlit as st

from nl_col_calc.utils.registry import CalcResultRegistry

from nl_col_calc.controller.benefits import benefits, name as benefits_name
from nl_col_calc.controller.energy import energy, name as energy_name
from nl_col_calc.controller.water import water, name as water_name
from nl_col_calc.controller.taxes import taxes, name as taxes_name
from nl_col_calc.controller.childcare import childcare, name as childcare_name
from nl_col_calc.controller.insurance import insurance, name as insurance_name
from nl_col_calc.controller.groceries import groceries, name as groceries_name
from nl_col_calc.controller.housing_rental import rental, name as rental_name

_calcs = {
    taxes_name: taxes,
    benefits_name: benefits,
    energy_name: energy,
    water_name: water,
    childcare_name: childcare,
    insurance_name: insurance,
    groceries_name: groceries,
    rental_name: rental,
}


def calc_choice():
    calculators = st.multiselect(
        'In order to make a more precise calculation please choose one or more calculators',
        _calcs
    )

    for k, v in _calcs.items():
        if k not in calculators:
            CalcResultRegistry().rem(k)

    return [_calcs[x] for x in calculators]

