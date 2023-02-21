import streamlit as st

from nl_col_calc.utils.emoji import emoji
from nl_col_calc.utils.registry import CalcResultRegistry


def notify_text(txt):
    st.markdown(f'  > {emoji.notification} Note: {txt}', unsafe_allow_html=True)


def calcresult(txt, add=None, sub=None, ignore_add_sub=False):
    st.markdown(f'### {txt}')

    if add:
        if isinstance(add, dict):
            for k, v in add.items():
                CalcResultRegistry().add(k, v)
        else:
            CalcResultRegistry().add(*add)

    if sub:
        if isinstance(sub, dict):
            for k, v in sub.items():
                CalcResultRegistry().sub(k, v)
        else:
            CalcResultRegistry().sub(*sub)

    #if not add and not sub and not ignore_add_sub:
    #    raise ValueError('Expected add or sub parameter')
