# municipal map - https://kadastralekaart.com/gemeenten

import re
import pandas as pd

from bs4 import BeautifulSoup

from nl_col_calc.utils.requests import req_get


def get_coelo_fields():
    req = req_get('https://www.coelo.nl/woonlasten/Lokale-lasten-calculator-2022-a.php')

    soup = BeautifulSoup(req.content)

    form = soup.find('form').find_all(['input', 'select'])

    retval = {}
    for el in form:
        if el.name.lower().strip() == 'select':
            retval[el['name']] = {
                'type': 'option',
                'name': el['name'],
                'options': {x['value']: x.text.strip() for x in el.find_all('option')}
            }
        elif el.name.lower().strip() == 'input':
            retval[el['name']] = {
                'type': 'text',
                'name': el['name'],
            }

    # return retval but skip keys ending in 2 as they are (at the moment of writing this code)
    # not required
    return {k: v for k, v in retval.items() if not k.endswith('2')}


def validate_coelo_form(coelo_fields, form):
    for k, v in form.items():
        if 'options' in coelo_fields[k]:
            if v not in coelo_fields[k]['options'].keys():
                return False

    return True


def get_coelo_taxes(gem_id, woningeigenaar, wozwaarde, huishouden, opcenten, elektrisch, gewicht, current_year=2022):
    url = f'https://www.coelo.nl/woonlasten/b{current_year}.php?gem_id1={gem_id}&woningeigenaar1={woningeigenaar}&wozwaarde1={wozwaarde}&huishouden1={huishouden}&opcenten1={opcenten}&elektrisch1={elektrisch}&gewicht1={gewicht}'

    req = req_get(url)

    soup = BeautifulSoup(req.content)

    for el in soup.find_all('td'):
        if 'colspan' in el.attrs:
            el['colspan'] = re.sub('[^0-9]', '', el['colspan'])

    dfs = pd.read_html(str(soup), thousands='.', decimal=',')
    dfs = [df.dropna(axis=0, how='all').reset_index() for df in dfs]

    dfs = [df[[0, 1, 2]] for df in dfs]

    dfs_extra = []
    dfs_out = []
    for i in range(len(dfs)):
        df = dfs[i]
        header_idx = df.index[df[1].str.startswith('Bedrag')][0]
        # df = df.rename(columns={k: v for k, v in df.loc[header_idx].to_dict().items() if pd.notna(v)})
        df = df.rename(columns={1: 'amount'})
        df = df.iloc[df.index.get_loc(header_idx) + 1:]
        df = df.set_index(0)
        df = df[df.columns[:-1]]
        df.index = df.index.rename('tax')
        df = df.replace('nvt', float('NaN'))

        df = df.drop(index=df.index[df.index.str.lower().str.contains('totale')])

        if df.index.str.lower().str.contains('hond').any():
            dfs_extra.append(df.index.rename('tariffs'))
        else:
            dfs_out.append(df.astype(float))

    if len(dfs_out) > 1:
        dfs_out = pd.concat(dfs_out)
    elif len(dfs_out) == 1:
        dfs_out = dfs_out[0]

    if len(dfs_extra) > 1:
        dfs_extra = pd.concat(dfs_extra)
    elif len(dfs_extra) == 1:
        dfs_extra = dfs_extra[0]

    return dfs_out, dfs_extra


# params = dict(
#     gem_id=1,
#     woningeigenaar='nee',
#     wozwaarde='',
#     huishouden='een',
#     opcenten='nee',
#     elektrisch='nee',
#     gewicht='',
# )
#
# validation = validate_coelo_form(**params)
# taxes = get_coelo_taxes(**params)
#
#
# coelo_fields = get_coelo_fields()
#
#
