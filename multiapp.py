import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

default_app_index = 0

class MultiApp :

    def __init__(self) :
        self.apps = []

    def add_app(self, title, func) :
        self.apps.append({
            "title": title,
            "function": func
        })

    def run(self):
        
        query_params = st.experimental_get_query_params()
        
        default_title = query_params["app"][0] if "app" in query_params else self.apps[default_app_index]["title"]
        default = next((i for i, item in enumerate(self.apps) if item["title"] == default_title), default_app_index)

        # st.sidebar.title("About")
        image = Image.open('logo.png')
        st.sidebar.image(image, width=150)
        
        st.sidebar.markdown(
            """
            This site is built and maintained by **Sergey Yurkov**. You can learn more about me at [linkedin.com](https://www.linkedin.com/in/sergeyyurkov1).
            """
        )
        # st.sidebar.info(
        #     """
        #     This project is built and maintained by **Sergey Yurkov**. You can learn more about me at [linkedin.com](#) and [dev.to](#).
        #     """
        # )

        st.sidebar.title("Navigation")
        app = st.sidebar.selectbox(
            "Select project",
            self.apps,
            index = default,
            format_func = lambda app : app["title"])

        if app :
            st.experimental_set_query_params( app = app["title"] )

        app["function"]()

        # st.markdown("""
        #     <script>
        #         window.onload = function() {
        #             var footer = document.getElementsByTagName("footer")[0];
        #             footer.innerHTML = "This project is built and maintained by Sergey Yurkov"
        #         }
        #     </script>
        # """, unsafe_allow_html=True)
