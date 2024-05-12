import streamlit as st
import pandas as pd
from pyOfferUp import fetch
import os
from offerup.c3 import C3, GRADES

# limit number of results that we actually display during testing
# to reduce db usage and app lag. need to fix c7/issues/7.
LIMIT = 15  # TODO remove in prod

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# Displaying the logo
img_col1, img_col2 = st.columns(2)
with img_col1:
    c3_path = os.path.join(SCRIPT_DIR, 'logos', 'c3logo.png')
    st.image(c3_path)
with img_col2:
    wb_path = os.path.join(SCRIPT_DIR, 'logos', 'webelogo.png')
    st.image(wb_path)

# Initializing the OfferUp C3 object
c3 = C3('conversations', 'offerup')

# Phones List Place Holder
PHONES = ["iphone 11", "iphone 12", "iphone 13", "iphone 14", "iphone 15"]  # TODO Get phones list from API


# Function to load data
def load_data():
    all_convos = c3.container.read_all_items()
    df = pd.DataFrame(all_convos)
    return df


# Loading data
data_load_state = st.text('Loading conversations...')
data = load_data()[:LIMIT]
data_load_state.text("Loading conversations... Done!")

# Checkbox to display raw data
if st.checkbox('`C3: conversations/offerup`'):
    st.subheader('Raw data')
    st.write(data)

# Number of containers
NUM_CONTAINERS = len(data)

# Initializing session state for expander expansion
if 'expand' not in st.session_state:
    st.session_state.expand = [True] + [False] * (NUM_CONTAINERS - 1)


# Function to collapse the current expander and expand the next one
def _next(i):
    st.session_state.expand[i] = False
    if i+1 < NUM_CONTAINERS:
        st.session_state.expand[i+1] = True


def _prev(i):
    st.session_state.expand[i] = False
    if i - 1 >= 0:
        st.session_state.expand[i - 1] = True


# Function to write listing details
def write_listing(i, _listing: dict):
    # Displaying listing title and price
    st.subheader(f'{_listing["originalTitle"]}: ${_listing["originalPrice"]}')
    # Displaying listing description
    st.write(_listing["description"])
    # Displaying listing photos
    photos = _listing["photos"]
    st.image([photo["detail"]["url"] for photo in photos])
    val_version = st.radio("Version", PHONES, horizontal=True, key=f"ver_{i}", index=None)
    val_grade = st.radio("Grade", GRADES, horizontal=True, key=f"grade_{i}", index=None)
    # Creating columns for different options
    st.markdown("<div style='padding-bottom: 0.25rem; font-size: 14px;'>Damage</div>", unsafe_allow_html=True)
    dmg_col1, dmg_col2, dmg_col3 = st.columns(3)
    with dmg_col1:
        val_back = st.checkbox("Cracked Back", key=f"back_{i}")
    with dmg_col2:
        val_cam = st.checkbox("Cracked Camera", key=f"cam_{i}")
    with dmg_col3:
        val_lcd = st.checkbox("LCD Damage", key=f"lcd_{i}")
    prog_col1, prog_col2 = st.columns(2)
    with prog_col1:
        st.button("Previous", on_click=_prev, args=(i,), key=f"prev_{i}", use_container_width=True)
    with prog_col2:
        st.button("Next", on_click=_next, args=(i,), key=f"next_{i}", use_container_width=True)
    # Returning selected values as a dictionary
    results = {'grade': val_grade, 'back_dmg': val_back, 'cam_dmg': val_cam, 'lcd_dmg': val_lcd,
               'itemType': val_version}
    return results


# Dictionary to store selected values for each listing
values = {}

# Iterate over data to display expanders
for idx, _id in enumerate(data.id):
    listing = fetch.get_listing_details(_id)["data"]["listing"]  # TODO Only getting intended listings
    with st.expander(f"Listing {listing['originalTitle']}  |  ID: {_id}", expanded=st.session_state.expand[idx]):
        values[_id] = write_listing(idx, listing)

# Button to print selected values
if st.button("Print Selected Grades", key="submit_button"):
    for _id, listing_body in values.items():
        if listing_body['grade'] is not None:
            print(f"Grade selected for Listing ID {_id}: {listing_body}")
            c3.update(_id, **listing_body)
