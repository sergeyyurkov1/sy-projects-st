import streamlit as st
from multiapp import MultiApp

# Sets Streamlit configuration, needs to run only once
st.set_page_config(page_title="Apps", page_icon="icon.png", layout="wide")

# Imports apps
from apps import home, anki_to_obsidian, bubble_pop

app = MultiApp()

# Hides developer menu and footer with CSS
# + additional scripts
st.markdown(
    """
    <style>
        #MainMenu {
        visibility: hidden;
        }
        /*footer {
        visibility: hidden;
        }*/
        button[title="View fullscreen"] {
        visibility: hidden;
        }
    </style>
    <script>
        // screen.orientation.lock("portrait-primary"); // Primarily for Bubble Pop! to prevent buggy behavior from changing device orientation
    </script>
    """, unsafe_allow_html=True)

# Apps init
app.add_app("Home", home.app)
app.add_app("Anki to Obsidian exporter", anki_to_obsidian.app)
app.add_app("Bubble Pop!", bubble_pop.app)

# Runs the MultiApp
app.run()
