import pandas
import streamlit as st
import pandas as pd
import numpy as np
import sys

from offerup.c3 import C3

st.title('*C3*')
c3 = C3('conversations', 'offerup')


# @st.cache_data
def load_data(nrows):
    all_convos = c3.container.read_all_items()
    df = pandas.DataFrame(all_convos)
    return df


data_load_state = st.text('Loading conversations...')
data = load_data(100)
data_load_state.text("Done! (using st.cache_data)")

st.subheader('Raw data')
st.write(data)
