import streamlit as st
import pandas as pd
from pyOfferUp import fetch

from offerup.c3 import C3, Grade

# Displaying the logo
st.image('https://i.imgur.com/uCGHEMh.png')

# Initializing the OfferUp C3 object
c3 = C3('conversations', 'offerup')

# Function to load data
def load_data():
    all_convos = c3.container.read_all_items()
    df = pd.DataFrame(all_convos)
    return df

# Loading data
data_load_state = st.text('Loading conversations...')
data = load_data()
data_load_state.text("Loading conversations... Done!")

# Checkbox to display raw data
if st.checkbox('`C3: conversations/offerup`'):
    st.subheader('Raw data')
    st.write(data)

# Create the expanders container
placeholder = st.empty()

# Number of containers
NUM_CONTAINERS = min(2, len(data))
CUR_PAGE = 0

# Phones List Place Holder
PHONES = ["iphone 11", "iphone 12", "iphone 13", "iphone 14", "iphone 15"] # TODO Get phones list from API

# Initializing session state for expander expansion
if 'expand' not in st.session_state:
    st.session_state.expand = [True] + [False] * (NUM_CONTAINERS - 1)

def clear_container(container):
    container.empty()

# Function to collapse the current expander and expand the next one
def next_exp(i):
    st.session_state.expand[i] = False
    if i+1 < NUM_CONTAINERS:
        st.session_state.expand[i+1] = True

def update_page(page_num):
    placeholder.empty()
    for i in range(NUM_CONTAINERS):
        index = page_num * NUM_CONTAINERS + i
        if index < len(data):
            _id = data.id[index]
            listing = fetch.get_listing_details(_id)["data"]["listing"]  # Fetching details for the listing
            with placeholder.empty():
                with st.expander(f"Listing {listing['originalTitle']}  |  ID: {_id}", expanded=st.session_state.expand[i]):
                    write_listing(index, listing)

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
    val_grade = st.radio("Grade", Grade._member_names_, horizontal=True, key=f"grade_{i}", index=None)
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
        st.button("Next", on_click=next_exp, args=(i,), key=f"next_{i}", use_container_width=True)
    with prog_col2:
        st.button("Previous", key=f"prev_{i}", use_container_width=True) # TODO add functionality
    # Returning selected values as a dictionary
    results = {'grade' : val_grade, 'back_dmg' : val_back, 'cam_dmg' : val_cam, 'lcd_dmg' : val_lcd, 'version' : val_version, }
    return results

# Dictionary to store selected values for each listing
values = {}

# Iterate over data to display expanders for the first page
for i in range(NUM_CONTAINERS):
    if i < len(data):
        _id = data.id[i]
        listing = fetch.get_listing_details(_id)["data"]["listing"] # Fetching details for the listing
        with st.empty():
            with st.expander(f"Listing {listing['originalTitle']}  |  ID: {_id}", expanded=st.session_state.expand[i]):
                write_listing(i, listing)

# Button to print selected values
foot_col1, foot_col2, foot_col3 = st.columns(3)
with foot_col1:
    if st.button("Print and go next", key="submit_button", use_container_width=True):
        for _id, value in values.items():
            if value is not None:
                print(f"Grade selected for Listing ID {_id}: {value}") # TODO Process Output
        CUR_PAGE += 1
        update_page(CUR_PAGE)
with foot_col2:
    if st.button("Previous Page", key="previous", use_container_width=True):
        CUR_PAGE -= 1
        update_page(CUR_PAGE)
with foot_col3:
    if st.button("Reset session state", key="session", use_container_width=True):
        st.session_state.expand = [True] + [False] * (NUM_CONTAINERS - 1)