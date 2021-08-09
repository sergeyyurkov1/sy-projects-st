import streamlit as st
from multiapp import MultiApp

# Sets Streamlit configuration, needs to run only once
st.set_page_config(page_title="Apps", layout="wide")
# page_icon="icon.png"

# Imports apps
from apps import home, anki_to_obsidian, bubble_pop, free_code_camp, vaccination_goals

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

# Register your app here
app.add_app("Home", home.app)
app.add_app("Anki to Obsidian exporter", anki_to_obsidian.app)
app.add_app("Bubble Pop!", bubble_pop.app)
app.add_app("freeCodeCamp Projects", free_code_camp.app)
app.add_app("Vaccination Goal Visualizer", vaccination_goals.app)

# Runs the MultiApp
app.run()
