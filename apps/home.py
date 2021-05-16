import streamlit as st
import streamlit.components.v1 as components
from .my_functions import load_static

import os
import pathlib

app_name = pathlib.Path(__file__).stem

print(os.path.join(app_name, "home.html"))

# print(os.path.basename(__file__))

def app():
    st.title('Blobby')
    st.markdown("""
    ***
    Made with `P5.js` JavaScript library
    """)

    html = load_static(os.path.join(app_name, "home.html")) + load_static(os.path.join(app_name, "style.css")) + load_static(os.path.join(app_name, "sketch.js"))

    components.html(html, height = 300)

    st.markdown("***")
    st.markdown("### [Source code](#)")
    st.code(load_static(os.path.join(app_name, "sketch.js"), False), language="javascript")
