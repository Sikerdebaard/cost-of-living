import streamlit as st

from nl_col_calc.utils.stutils import notify_text, calcresult

import statsmodels.api as sm
from pathlib import Path
from datetime import date
import pandas as pd


name = "Housing (rental)"


@st.cache_resource(ttl=86400)  # cache ~1 day
def get_latest_model():
    indir = Path('data/')

    # model files are in iso dateformat so we can just sort them easily
    model_files = list(sorted(indir.glob('*-model-reduced.pickle')))

    # pick the latest model
    model = sm.load(model_files[-1])
    dt = model_files[-1].name[:10]

    return model, dt 


def get_supported_places():
    model, dt = get_latest_model()

    return [str(x)[6:].replace('den', 'den ').title() for x in model.params.index if str(x).startswith('B-cit-')]


def predict(city, m2, garden, parking, upholstry):
    model, model_update_dt = get_latest_model()
    df_pred = pd.DataFrame(index=[], columns=model.params.index)

    df_pred.loc[0] = 0
    df_pred.loc[0, 'const'] = 1

    city = city.lower().replace(' ', '').strip()

    df_pred.loc[0, f'B-cit-{city}'] = 1
    df_pred.loc[0, f'F-m2-{city}'] = m2

    df_pred.loc[0, 'B-out-garden'] = 1 if garden else 0
    df_pred.loc[0, 'B-par-aanwezig'] = 1 if garden else 0

    st.write(upholstry)
    if upholstry == 'furnished':
        df_pred.loc[0, 'B-tra-interieur__gemeubileerd'] = 1
    elif upholstry == 'upholstered':
        df_pred.loc[0, 'B-tra-interieur__gestoffeerd'] = 1


    pred = model.get_prediction(df_pred)
    df_summary = pred.summary_frame(alpha=0.05)

    return df_summary.iloc[0]


def rental():
    st.header('Housing (rental)')

    model, model_update_dt = get_latest_model()

    notify_text(f'The Netherlands is currently going through a housing crisis. Because of this housing is scarce and relatively expensive in most places. One of the biggest websites for finding rentals in the Netherlands is [Pararius](https://www.pararius.nl/)<br> This tool uses a model-based approach to estimate how much budget you need based on input criteria of your desired housing. That does not mean that housing with those criteria exists or is available for rent - it just gives you an approximation of how much it would cost if it is. The models data was last updated on {model_update_dt}.')

    city = st.selectbox('Please choose a population center supported by this tool:', get_supported_places())

    notify_text('There is a strong correlation between m² and number of rooms - hence the tool only asks for desired m². For each room add approx. 20 to 25 m² extra.')
    m2 = st.number_input('How many m² of space should the rental unit have?', min_value=0, value=55)

    garden = st.checkbox('Do you wish to have a garden?', False)
    #parking = st.checkbox('Should the rental unit come with a designated parking lot?', False)
    parking = False

    notify_text('By default most housing in the Netherlands comes without a floor installed. If you wish to rent a place with a floor you should look for an upholstered or furnished place.')
    upholstry = st.radio('Do you wish to rent an unfurnished (kaal), upholstered (gestoffeerd) or furnished (gemeubileerd) appartment?', ['unfurnished', 'upholstered', 'furnished'], index=2)

    pred = predict(city, m2, garden, parking, upholstry)

    budget = st.number_input('How much budget do you wish to allocate for housing rental per month in euros?', min_value=0, value=int(pred["mean"]))
    
    calcresult(f'Based on your inputs the budget needed for housing is between €{pred["mean_ci_lower"]:.00f} - €{pred["mean_ci_upper"]:.00f} with a mean at €{pred["mean"]:.00f} and a StdErr of €{pred["mean_se"]:.00f}', sub=[name, budget])
    
    notify_text(f'Many landlords ask for a 2x to 4x salary income as compared to the monthly rental price. An income of €{budget*2} - €{budget*4} would be advisable to increase your odds of finding housing.')

    
