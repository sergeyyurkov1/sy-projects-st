import streamlit as st
import streamlit.components.v1 as components

# Application requirements
import io
from io import StringIO
import re
import base64
import time

# Defines the application
def app():
    st.title("Anki to Obsidian exporter")
    st.subheader("Export your flashcards to Obsidian note taking app.")
    # st.markdown("***")

    col1, col2 = st.columns((1, 1))

    with col1:
        options = st.expander("Options", False)
        option = options.radio("Select your Anki card format", ["Basic"])

    # with col3:
    #     # fmt: off
    #     st.markdown(
    #         """
    #             #### How to import data
    #             Coming soon...
    #         """
    #     )
    #     # fmt: on


    with col2:
        uploaded_file = st.file_uploader(
            "Choose your export file",
            type="txt",
            accept_multiple_files=False,
            key=None,
            help=None,
        )

    st.markdown("***")

    col3, col4 = st.columns((1, 1))

    if uploaded_file is not None:
        with col3:
            with st.spinner(text="Loading preview..."):
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                string_data = stringio.read()
                stringio.close()

                st.header("Before preview")
                st.write(string_data.split("\n")[:5])

            if re.search(r"^(.*)\t(.*)\t(.*)", string_data) == None:
                st.error("Please check if you exported the file per instructions")
                st.stop()

            out = re.sub(
                r"^(.*)\t(.*)\t(.*)",
                rf"START\n{option}\n\1\nBack: \2\nTags: \3\nEND\n\n",
                string_data,
                flags=re.MULTILINE,
            )

            st.success("Conversion success")

        with col4:
            with st.spinner(text="Preparing download..."):
                time.sleep(4)

                output = StringIO()
                output.write(out)

                o = output.getvalue()

                b64 = base64.b64encode(
                    o.encode()
                ).decode()  # some strings <-> bytes conversions necessary here
                href = f'<a href="data:file/txt;base64,{b64}" download="anki-{option.lower()}.md">Download Markdown</a>'

                st.markdown(href, unsafe_allow_html=True)

                output.close()

            with st.spinner(text="Loading preview..."):
                time.sleep(4)

                st.header("After preview")
                st.write(out.split("\n\n")[:5])