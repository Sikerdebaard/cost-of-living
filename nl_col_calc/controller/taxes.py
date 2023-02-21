import streamlit as st

from nl_col_calc.calculators.taxes import get_coelo_fields, validate_coelo_form, get_coelo_taxes
from nl_col_calc.utils.pandas_style import stylize
from nl_col_calc.utils.stutils import calcresult, notify_text

name = 'Taxes (local + national)'

_form = {}

_vals_yesno = {
    'Yes': 'ja',
    'No': 'nee',
}

@st.cache_data
def _coelo_fields():
    return get_coelo_fields()


@st.cache_data
def _coelo_taxes(**kwargs):
    return get_coelo_taxes(**kwargs)


def _gem():
    fid = 'gem_id1'

    vals = {v: k for k, v in _coelo_fields()[fid]['options'].items()}

    _form[fid] = vals[st.selectbox(
        'Select the municipality where you are planning to live',
        vals,
    )]

    st.markdown('Municipality map: https://kadastralekaart.com/gemeenten')


def _woningeigenaar():
    fid = 'woningeigenaar1'

    vals = {'Rent': 'nee', 'Buy': 'ja'}
    _form[fid] = vals[st.selectbox(
        'Are you planning to rent or buy housing?',
        vals,
        index=0,
    )]


def _wozwaarde():
    fid = 'wozwaarde1'

    if _form['woningeigenaar1'] != 'ja':
        _form[fid] = None
        return

    _form[fid] = st.number_input(
        'You are buying: what is the upper limit of your budget?',
        min_value=100_000,
        step=50_000,
        value=450_000,
    )

def _huishouden():
    fid = 'huishouden1'

    vals = {
        '1': 'een',
        '2': 'twee',
        '3': 'drie',
        '4+': 'vier',
    }

    _form[fid] = vals[st.selectbox(
        'How many people will be registered in the household?',
        vals,
        index=0,
    )]


def _opcenten():
    fid = 'opcenten1'

    _form[fid] = _vals_yesno[st.selectbox(
        'Are you planning to own a car?',
        _vals_yesno,
        index=1,
    )]


def _elektrisch():
    fid = 'elektrisch1'

    if _form['opcenten1'] != 'ja':
        _form[fid] = _vals_yesno['No']
        return

    _form[fid] = _vals_yesno[st.selectbox(
        'Are you planning to own an electric car?',
        _vals_yesno,
        index=1
    )]



def _gewicht():
    fid = 'gewicht1'

    if _form['opcenten1'] != 'ja' or _form['elektrisch1'] != 'nee':
        _form[fid] = None
        return

    _form[fid] = st.number_input(
        'What is the weight (in KG) of the car?',
        step=100,
        min_value=500,
        value=1500,
    )



def taxes():
    st.header(name)

    fields = _coelo_fields()

    assert len(set(fields.keys()).difference(_coelo_mappings.keys())) == 0

    for k, f in _coelo_mappings.items():
        f()


    if not validate_coelo_form(_coelo_fields(), _form):
        st.error('Error: form values invalid')
        return

    taxes = _coelo_taxes(**{k.strip('1'): v for k, v in _form.items()})

    df = taxes[0].dropna()
    df.columns = ['amount / year']

    yearly_local_taxes = df.sum().sum()
    monthly = yearly_local_taxes / 12

    calcresult(f'Estimated monthly local and national taxes: €{monthly:.00f}.', sub=[name, monthly] if monthly > 0 else None)

    st.dataframe(stylize(df.apply(lambda x: x.apply(lambda y: f'€{y:.00f}'))))


_coelo_mappings = {
    'gem_id1': _gem,
    'woningeigenaar1': _woningeigenaar,
    'wozwaarde1': _wozwaarde,
    'huishouden1': _huishouden,
    'opcenten1': _opcenten,
    'elektrisch1': _elektrisch,
    'gewicht1': _gewicht,
}
