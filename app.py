import streamlit as st

from io import BytesIO

from nl_col_calc.controller.calc_choice import calc_choice
from nl_col_calc.controller.ppp import ppp
from nl_col_calc.utils.emoji import emoji
from nl_col_calc.utils.stutils import notify_text
from nl_col_calc.utils.registry import CalcResultRegistry
from nl_col_calc.utils.pandas_style import stylize


def init():
    if not hasattr(st.session_state, 'init'):
        st.session_state.init = True

        # st.session_state.salt = 2.


def page():
    st.title('Netherlands Cost of Living Calculator')
    notify_text('Numbers indicated by this tool are indications only. No rights can be derived from this information.')
    notify_text('This tool does not store or collect any data. If you wish to store your results you can export to Excel worksheet at the bottom of this page.')

    ppp()

    calcs = calc_choice()

    for calc in calcs:
        calc()

    reg = CalcResultRegistry()
    res = reg.get()
    if res is not None and res.index.shape[0] > 0:
        st.header('Total monthly benefits and expenses:')
        st.write(stylize(res))
        st.write(f'Based on this you need a minimum of €{-(res["benefits"].fillna(0).sum() - res["expenses"].fillna(0).sum()):.00f} income after taxes a month')

        memxls = BytesIO()
        res.to_excel(memxls, index_label="name")  # write to BytesIO buffer
        memxls.seek(0) 

        st.download_button(
            label="Download Excel workbook",
            data=memxls,
            file_name="results.xlsx",
            mime="application/vnd.ms-excel"
        )


if __name__ == '__main__':
    st.set_page_config(
         page_title="Netherlands Cost of Living Calculator",
         page_icon=emoji.page_emoji,
         layout="wide",
         initial_sidebar_state="expanded",
         menu_items={
             #'Get Help': 'https://www.extremelycoolapp.com/help',
             #'Report a bug': "https://www.extremelycoolapp.com/bug",
             #'About': "# This is a header. This is an *extremely* cool app!"
         }
     )

    init()
    page()

