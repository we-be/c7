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

def write_listing(expander, radio_key, _id, _listing: dict):
    expander.subheader(f'{listing["originalTitle"]}: ${listing["originalPrice"]}')
    expander.write(listing["description"])
    selected_grade = expander.radio("Grade", Grade._member_names_, horizontal=True, key=radio_key, index=None)
    print(selected_grade)
    photos = listing["photos"]
    expander.image([photo["detail"]["url"] for photo in photos])
    return selected_grade

selected_grades = {}

for _id in data.id:
    listing = fetch.get_listing_details(_id)["data"]["listing"]
    radio_key = f"grade_{_id}"
    if radio_key not in st.session_state:
        st.session_state[radio_key] = True
    expander = st.expander(f"Listing {listing['originalTitle']}  |  ID: {_id}", expanded=st.session_state[radio_key])
    selected_grades[_id] = write_listing(expander, radio_key, _id, listing)

if st.button("Print Selected Grades", key="submit_button"):
    for _id, grade in selected_grades.items():
        if grade is not None:
            print(f"Grade selected for Listing ID {_id}: {grade}")
