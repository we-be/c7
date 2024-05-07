import streamlit as st
import pandas as pd
import time
from pyOfferUp import fetch

from offerup.c3 import C3, Grade

st.image('https://i.imgur.com/uCGHEMh.png')
c3 = C3('conversations', 'offerup')

# Phones List Place Holder
PHONES = ["iphone 11", "iphone 12", "iphone 13", "iphone 14", "iphone 15"]

# Function to load data
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

NUM_CONTAINERS = len(data)

if 'expand' not in st.session_state:
    st.session_state.expand = [True] + [False] * (NUM_CONTAINERS - 1)

# Function to collapse the current expander and expand the next one
def _next(i):
    print("test")
    st.session_state.expand[i] = False
    if i+1 < NUM_CONTAINERS:
        st.session_state.expand[i+1] = True

# Function to write listing details
def write_listing(i, _listing: dict):
    st.subheader(f'{_listing["originalTitle"]}: ${_listing["originalPrice"]}')
    st.write(_listing["description"])
    col1, col2, col3 = st.columns(3)
    with col1:
        val_grade = st.radio("Grade", Grade._member_names_, key=f"grade_{i}", index=None)
    with col2:
        st.markdown("<div style='padding-bottom: 0.25rem; font-size: 14px;'>Damage</div>", unsafe_allow_html=True)
        val_back = st.checkbox("Cracked Back", key=f"back_{i}")
        val_cam = st.checkbox("Cracked Camera", key=f"cam_{i}")
        val_lcd = st.checkbox("LCD Damage", key=f"lcd_{i}")
    with col3:
        val_version = st.selectbox("Version", PHONES, key=f"ver_{i}", placeholder=PHONES[0]) # TODO Replace placeholder with value of phone
        st.button("Next", on_click=_next, args=(i,), key=f"next_{i}")
    photos = _listing["photos"]
    st.image([photo["detail"]["url"] for photo in photos])
    results = {'grade' : val_grade, 'back_dmg' : val_back, 'cam_dmg' : val_cam, 'lcd_dmg' : val_lcd, 'version' : val_version, }
    return results

values = {}

# Iterate over data to display expanders
for i, _id in enumerate(data.id):
    listing = fetch.get_listing_details(_id)["data"]["listing"]
    with st.expander(f"Listing {listing['originalTitle']}  |  ID: {_id}", expanded=st.session_state.expand[i]):
        values[_id] = write_listing(i, listing)

if st.button("Print Selected Grades", key="submit_button"):
    for _id, value in values.items():
        if value is not None:
            print(f"Grade selected for Listing ID {_id}: {value}")