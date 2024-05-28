import os

import streamlit as st
import pandas as pd
from pyOfferUp import fetch
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from offerup.c3 import C3, GRADES
from offerup.config import PHONES
from offerup.colorize import cprint

# limit number of results that we actually display during testing
LIMIT = 20  # TODO add a "load" button to paginate
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


# Function to load data
def load_data():
    all_convos = c3.get_ungraded(LIMIT)
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


def update_df():
    listings_df = pd.DataFrame(columns=['id', 'title', 'price', 'description', 'item_type', 'photo_urls'])
    listing_details_list = []
    phones_dict = {phone: i + 1 for i, phone in enumerate(PHONES)}
    for index, row in data.iterrows():
        listing_details = fetch.get_listing_details(row['id'])["data"]["listing"]
        item_type = row['itemType']
        item_index = phones_dict.get(item_type, None)
        listing_details_list.append({'id': row['id'],
                                     'title': listing_details['title'],
                                     'price': listing_details['price'],
                                     'description': listing_details['description'],
                                     'item_index': item_index,
                                     'photo_urls': [photo["detail"]["url"] for photo in listing_details["photos"]]})
    # Convert the list of dictionaries to a DataFrame
    new_listings_df = pd.DataFrame(listing_details_list)
    # Concatenate the new DataFrame with the existing DataFrame
    listings_df = pd.concat([listings_df, new_listings_df], ignore_index=True)
    return listings_df


def init_session():
    if 'listings_df' not in st.session_state:
        st.session_state.listings_df = update_df()


# Dictionary to store selected values for each listing
values = {}
init_session()
NUM_CONTAINERS = sum(pd.notna(item_index) for item_index in st.session_state.listings_df['item_index'])

# Initializing session state for expander expansion
if 'expand' not in st.session_state:
    st.session_state.expand = [True] + [False] * (NUM_CONTAINERS - 1)


# Function to collapse the current expander and expand the next one
def _next(i):
    st.session_state.expand[i] = False
    if i + 1 < NUM_CONTAINERS:
        st.session_state.expand[i + 1] = True


# Function to write listing details
def write_listing(i, item_index, _exp_count):
    listing = st.session_state.listings_df.iloc[i]  # Fetch the listing from the DataFrame
    # Displaying listing title and price
    st.subheader(f'{listing["title"]}: ${listing["price"]}')
    # Displaying listing description
    st.write(listing["description"])
    # Displaying listing photos (assuming 'photo_url' is a URL to the photo)
    st.image(listing["photo_urls"])
    val_item_type = st.radio("Device", ["bad device"] + PHONES, horizontal=True, key=f"ver_{i}", index=item_index)
    val_grade = st.radio("Grade", GRADES, horizontal=True, key=f"grade_{i}", index=1)
    # Creating columns for different options
    st.markdown("<div style='padding-bottom: 0.25rem; font-size: 14px;'>Damage</div>", unsafe_allow_html=True)
    back_col, cam_col = st.columns(2)
    with back_col:
        with st.container(border=True):
            val_back = st.checkbox("Cracked Back", key=f"back_{i}")
    with cam_col:
        with st.container(border=True):
            val_cam = st.checkbox("Cracked Camera", key=f"cam_{i}")
    bat_col, lock_col = st.columns(2)
    with bat_col:
        with st.container(border=True):
            val_lcd = st.checkbox("Battery Damage", key=f"lcd_{i}")
    with lock_col:
        with st.container(border=True):
            val_lock = st.checkbox("ICloud Lock", key=f"lock_{i}")
    st.button("Next", on_click=_next, args=(_exp_count,), key=f"next_{i}", use_container_width=True)
    # Returning selected values as a dictionary
    results = {
        'grade': val_grade,
        'back_dmg': val_back,
        'cam_dmg': val_cam,
        'bat_dmg': val_lcd,
        'lock': val_lock,
        'itemType': val_item_type,
    }
    return results


exp_count = 0
# Iterate over data to display expanders
for idx in range(min(NUM_CONTAINERS, len(st.session_state.listings_df))):
    item_index = st.session_state.listings_df.iloc[idx]['item_index']
    if pd.notna(item_index):
        item_index = int(item_index)
        with st.expander(f"Listing {st.session_state.listings_df.iloc[idx]['title']}  |  ID: {st.session_state.listings_df.iloc[idx]['id']}",
                         expanded=st.session_state.expand[exp_count]):
            values[st.session_state.listings_df.iloc[idx]['id']] = write_listing(idx, item_index, exp_count)
        exp_count += 1

# Button to print selected values
if st.button("Save Changes", key="submit_button", use_container_width=True):
    for _id, listing_body in values.items():
        if listing_body['grade'] is not None:
            print(f"Grade selected for Listing ID {_id}: {listing_body}")

            # we wrap the call to update the db in try-except here
            # because somehow when Ed saves it tries to update some resources that don't exist
            # but... we don't want to prevent the app from completely saving
            # ideally we want to triage this at some point in the future
            try:
                c3.update(_id, **listing_body)
            except CosmosResourceNotFoundError as e:
                cprint('red', f'COULD NOT UPDATE LISTING {_id}: {e}')

    st.session_state.listings_df = update_df()
