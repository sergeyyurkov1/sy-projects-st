# import ptvsd
# ptvsd.enable_attach(address=("localhost", 5678))
# ptvsd.wait_for_attach() # Only include this line if you always want to attach the debugger

import streamlit as st
from PIL import Image

# Sets Streamlit configuration
st.set_page_config(page_title="Apps", layout="wide", page_icon="01.png")

# Imports apps
from apps import (
    home,
    anki_to_obsidian,
    bubble_pop,
    free_code_camp,
    vaccination_goals
)
apps = {
    "Home": home.app, # Home
    "Anki to Obsidian exporter": anki_to_obsidian.app,
    "Bubble Pop!": bubble_pop.app,
    # "freeCodeCamp Projects": free_code_camp.app,
    "Vaccination Goal Visualizer": vaccination_goals.app,
}
app_titles = list(apps.keys())

def main():
    """
    App entry point
    """
    # Sidebar
    # -------
    image = Image.open("01.png")
    st.sidebar.image(image, width=150)
    
    st.sidebar.markdown(
        """
        This site is built and maintained by **Sergey Yurkov**. You can learn more about me at [linkedin.com](https://www.linkedin.com/in/sergeyyurkov1).
        """
    )

    if len(app_titles) != 0:
        query_params = st.experimental_get_query_params()
        app_title = query_params["app"][0] if "app" in query_params else app_titles[0]

        # st.sidebar.selectbox() requires default 'index'
        try:
            index = app_titles.index(app_title)
        except ValueError:
            index = 0
        selected_app = st.sidebar.selectbox("Select a project", app_titles, index)
        
        # Runs selected app
        apps[selected_app]()

        # st.experimental_set_query_params() # app=selected_app
    else:
        st.warning("404")

# Hides developer menu and footer with CSS
# + additional scripts
st.markdown(
    """
    <style> 
        .css-ypaiy1 {
        visibility: hidden;
        }
        #MainMenu {
        visibility: hidden;
        }
        footer {
        visibility: hidden;
        }
        button[title="View fullscreen"] {
        visibility: hidden;
        }
    </style>
    <script>
        // screen.orientation.lock("portrait-primary"); // Primarily for Bubble Pop! to prevent buggy behavior from changing device orientation
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()