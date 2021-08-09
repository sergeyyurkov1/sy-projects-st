import streamlit as st
import streamlit.components.v1 as components

# Defines the application
def app():
    st.title("freeCodeCamp Projects")
    st.subheader("Some of my projects for Scientific Computing with Python and Data Analysis with Python certification programs")
    st.markdown("***")

    st.markdown("## Sea Level Predictor")
    components.iframe("https://replit.com/@sergeyyurkov1/boilerplate-sea-level-predictor?lite=true", width=800, height=600)
    # embed=true
    st.markdown("***")

    st.markdown("## Time Series Visualizer")
    components.iframe("https://replit.com/@sergeyyurkov1/boilerplate-page-view-time-series-visualizer?lite=true", width=800, height=600)
    # embed=true
    st.markdown("***")

    st.markdown("## Medical Data Visualizer")
    components.iframe("https://replit.com/@sergeyyurkov1/boilerplate-medical-data-visualizer?lite=true", width=800, height=600)
    # embed=true
    st.markdown("***")

    st.markdown("## Demographic Data Analyzer")
    components.iframe("https://replit.com/@sergeyyurkov1/boilerplate-demographic-data-analyzer?lite=true", width=800, height=600)
    # embed=true
    st.markdown("***")

    st.markdown("## Mean, Variance, Standard Deviation Calculator")
    components.iframe("https://replit.com/@sergeyyurkov1/boilerplate-mean-variance-standard-deviation-calculator?lite=true", width=800, height=600)
    # embed=true
    st.markdown("***")

    st.markdown("## Probability Calculator")
    components.iframe("https://replit.com/@sergeyyurkov1/boilerplate-probability-calculator?lite=true", width=800, height=600)
    # embed=true
