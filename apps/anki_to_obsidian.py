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
    st.title('Anki to Obsidian exporter')
    st.subheader("Export your flashcards to Obsidian note taking app.")
    st.markdown("***")

    # st.sidebar.markdown("***")
    # add_selectbox = st.sidebar.selectbox("How would you like to be contacted?", ("Email", "Home phone", "Mobile phone"))

    col1, col2, col3 = st.columns([3,1,2])

    with col2 :
        st.write("")
    
    with col3 :
        # st.markdown("""
        # #### How to import data
        # """)
        st.write("")

    with col1 :
        options = st.expander("Options", False)
        option = options.radio("Select your Anki card format", ["Basic"])

        st.markdown("***")

        uploaded_file = st.file_uploader("Choose your export file", type="txt", accept_multiple_files=False, key=None, help=None)

        if uploaded_file is not None:

            with st.spinner(text="Loading preview...") :
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                string_data = stringio.read()
                stringio.close()

                st.markdown("***")
                st.header("Data preview")
                st.write(string_data.split('\n')[:5])
            
            if re.search(r"^(.*)\t(.*)\t(.*)", string_data) == None :
                st.error("Please check if you exported the file per instructions")
                st.stop()

            out = re.sub(r"^(.*)\t(.*)\t(.*)", fr"START\n{option}\n\1\nBack: \2\nTags: \3\nEND\n\n", string_data, flags=re.MULTILINE)
            
            st.success('Conversion success')

            with st.spinner(text="Loading preview...") :
                time.sleep(4)

                st.markdown("***")
                st.header("Download preview")
                st.write(out.split('\n\n')[:5])

                output = StringIO()
                output.write(out)

                o = output.getvalue()
            
            
            with st.spinner(text="Preparing download...") :
                time.sleep(4)

                b64 = base64.b64encode(o.encode()).decode()  # some strings <-> bytes conversions necessary here
                href = f'<a href="data:file/txt;base64,{b64}" download="anki-{option.lower()}.md">Download Markdown</a>'

                st.markdown("***")
                st.markdown(href, unsafe_allow_html=True)

                output.close()
