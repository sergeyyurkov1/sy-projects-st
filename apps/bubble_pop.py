import streamlit as st
import streamlit.components.v1 as components
# import pathlib
# import os
from streamlit import caching

caching.clear_cache()

# from .my_functions import load_static

# STREAMLIT_STATIC_PATH = pathlib.Path(st.__path__[0]) / "static"
# app_name = pathlib.Path(__file__).stem

def app():
    st.title('Bubble Pop!')
    st.markdown("""
    ***
    Simple and relaxing game made with `P5.js` and `Matter.js` libraries. Pop some bubbles but watch out for pesky donuts! And remember: "It's not a bug, it's a feature!"
    
    *Runs best on Chrome/Chromium based browsers*
    """)

    components.iframe("https://sy-static-st.herokuapp.com/bubble_pop", width=800, height=600)

    # html = load_static(os.path.join(STREAMLIT_STATIC_PATH, app_name, "index.html"))
    # components.html(html, width=800, height = 600)

    st.markdown("***")
    st.markdown("### [Source code](https://github.com/sergeyyurkov1/sy-static-st/tree/main/static/bubble_pop)")
