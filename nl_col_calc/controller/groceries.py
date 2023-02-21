import streamlit as st

from nl_col_calc.utils.stutils import calcresult, notify_text


name = 'Groceries'

def groceries():
    st.header('Groceries')

    approx_fam_two = 120

    notify_text('The Netherlands does not have an eating out culture. In general eating out is only considered for special occasions. Most Dutch people cook their meals at home. There is usually only one hot meal. Breakfast and lunch are usually light and are usually sandwiches while dinner is a bigger hot meal.')

    notify_text(f'The two largest supermarket chains in the Netherlands are AH and Jumbo. Next to this are the German supermarkets that have the reputation of being cheaper. Those are Lidl and Aldi. Please go to [AH](https://www.ah.nl/) and/or [Jumbo](https://www.jumbo.com/) to do some virtual shopping. Collect some data on the price of the groceries that you would typically buy and fill the numbers in the form below. A rough approximation of the average Dutch family of two is €{approx_fam_two} per week.')

    groceries = st.number_input('How many € / week are you planning to spend on groceries?', min_value=0, value=approx_fam_two)

    res = groceries * 52 / 12

    calcresult(f'Estimated monthly expenses on groceries: €{res:.00f}.', sub=[name, res] if res > 0 else None)
