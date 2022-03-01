import streamlit as st
import streamlit.components.v1 as components
from functions import functions

# import os
from pathlib import Path

# print(os.path.basename(__file__))
app_name = Path(__file__).stem

def app():
    st.markdown("""
    # Home
    ***
    Meet Blobby. It is made with `P5.js` JavaScript library!
    """)

    # import requests
    # try:
    #     requests.get("http://www.google.com")
    # except:
    #     st.error("Something went wrong. Please try again later.")
    #     st.stop()

    with st.spinner(text="Loading..."):
        html = functions.load_static("home.html") + functions.load_static("style.css") + functions. load_static("sketch.js")

        components.html(html, height = 300)

        st.markdown("***")
        st.markdown("### [Source code](#)")
        st.code(functions.load_static("sketch.js", False), language="javascript")
