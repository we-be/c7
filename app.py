from typing import Optional

import streamlit as st
import pandas as pd
from pyOfferUp import fetch

from offerup.c3 import C3, Grade

st.image('https://i.imgur.com/uCGHEMh.png')
c3 = C3('conversations', 'offerup')


# @st.cache_data
def load_data():
    all_convos = c3.container.read_all_items()
    df = pd.DataFrame(all_convos)
    return df


data_load_state = st.text('Loading conversations...')
data = load_data()
data_load_state.text("Loading conversations... Done!")

if st.checkbox('`C3: conversations/offerup`'):
    st.subheader('Raw data')
    st.write(data)


def write_listing(_listing: dict):
    st.subheader(f'{listing["originalTitle"]}: ${listing["originalPrice"]}')
    st.write(listing["description"])
    st.radio("Grade", Grade._member_names_, horizontal=True, key=_id)

    photos = listing["photos"]
    st.image([photo["detail"]["url"] for photo in photos])


for _id in data.id:
    listing = fetch.get_listing_details(_id)["data"]["listing"]
    st.sidebar.selectbox = listing["originalTitle"]
    write_listing(listing)
