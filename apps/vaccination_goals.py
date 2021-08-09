import streamlit as st
import streamlit.components.v1 as components

# Defines the application
def app():
    import humanize
    import pandas as pd
    import numpy as np
    from datetime import date
    from datetime import datetime
    from datetime import timedelta
    import plotly.express as px
    import plotly.graph_objects as go
    
    demographic_data = "https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/EXCEL_FILES/1_Population/WPP2019_POP_F01_1_TOTAL_POPULATION_BOTH_SEXES.xlsx"
    vaccination_data = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv"

    # col1, col2, col3 = st.columns([1,10,1])

    # with col1 :
    #     st.write("")
    
    # with col3 :
    #     st.write("")

    @st.cache
    def load_vaccination_data():
        df = pd.read_csv(vaccination_data, usecols=["date", "location", "daily_vaccinations"], parse_dates=["date"])
        return df

    # Selects country population
    # @st.cache
    def get_population(country: str, year: str) -> dict:
        df1 = pd.read_excel(demographic_data)

        # Removes first 14 rows containing unrelated information
        df1 = df1.iloc[15:]

        # Sets the first row as column names
        df1.columns = df1.iloc[0]

        # Removes the first row containing column names as it is no longer needed
        df1 = df1.iloc[1:]

        population = {}
        try:
            # population["population"] = df1.loc[ df1[df1.columns[2]] == country, year ].values[0] * 1000
            population["population"] = df1.loc[ df1[df1.columns[2]].str.contains(country), year ].values[1] * 1000
        except:
            st.error(f"Something went wrong when looking up data for {country}. Please select a different location. I am working on a solution.")
            st.stop()
        
        return population

    # with col2 :
    st.title("Vaccination Goal Visualizer")
    st.markdown("""
        This app approximates a date when our global vaccination goals will be achieved; data is updated every day and automatically reflected in charts.
        * **Data sources:** [Our World In Data](https://ourworldindata.org/covid-vaccinations), [United Nations](https://population.un.org/wpp)
        * **Disclaimer:** *work in progress; vaccination data in certain regions is reported inconsistently; plot figures are estimated and can not be fully accurate*
    """)
    st.markdown("*Due to some scaling issues, if on mobile, please run in landscape mode*")

    year = "2020"

    with st.spinner(text="Loading vaccination data...") :
        df_vaccination_data_raw = load_vaccination_data()

    sorted_unique_locations = sorted(df_vaccination_data_raw.location.unique())

    locations = st.multiselect("Select location(s)", sorted_unique_locations)

    # @st.cache
    def plot_data(df_grouped, country_info):
        for c in country_info:
            country = df_grouped.get_group(c)

            # Annotations to display
            days_to_goal = int(country_info[c]["days_to_goal"])
            goal_vaccinations = int(country_info[c]["goal_vaccinations"])
            population = int(country_info[c]["population"])
            date = country_info[c]["date"]
            daily_vaccinations = int(country_info[c]["daily_vaccinations"])
            vaccinated_people = int(country_info[c]["vaccinated_people"])
            goal_date = country_info[c]["goal_date"]

            vacc_start_date = country.iloc[0,1]
            print(vacc_start_date)

            fig = px.bar(country, x="date", y="daily_vaccinations_cumsum", labels={
                            "date": "Days",
                            "daily_vaccinations_cumsum": "Vaccinations done (cumulative sum)"},
                        title=f"{c}"
            )

            fig.update_traces(marker_color="#9481d2", hovertemplate="%{y:,}")

            fig.update_layout({
                "plot_bgcolor": "#f5f7f3",
                "paper_bgcolor": "#f5f7f3"}, hovermode="x", hoverlabel=dict(font_color="white")
            )

            fig.add_annotation(
                text=f"<b>Vaccination goal</b><br>70% / 2 doses<br>in <b>{days_to_goal} days ({goal_date:%B %Y})</b>",
                align="left",
                x=country_info[c]["goal_date"],
                y=country_info[c]["goal_vaccinations"],
                font_color="Red",
                arrowcolor="Red",
                arrowhead=1,
                hovertext=f"~ {humanize.intword(goal_vaccinations)} doses required",
                showarrow=False,
                # yanchor="top",
                xanchor="left",
                xshift=10
            )

            fig.add_annotation(text=f"<b>Population:</b> {population:,} ({year})<br><b>Vaccination started:</b> {vacc_start_date:%B %d, %Y}<br><br><b>As of {date:%B %d, %Y}:</b> {vaccinated_people:,} ({int(vaccinated_people*100/population)}%) people received at least 2 doses of vaccine with<br>{daily_vaccinations:,} shots being administered daily",
                align="left",
                xref="paper", yref="paper",
                x=0.1, y=0.9,
                showarrow=False,
                bgcolor="rgba(0,0,0,0)"
            )

            fig.add_shape(type="line",
                x0=country_info[c]["date"], y0=country_info[c]["daily_vaccinations_cumsum"], x1=country_info[c]["goal_date"], y1=country_info[c]["goal_vaccinations"],
                line=dict(
                    color="Red",
                    width=1,
                    dash="dot"
                )
            )

            fig.add_shape(type="line",
                x0=country_info[c]["goal_date"], y0=0, x1=country_info[c]["goal_date"], y1=country_info[c]["goal_vaccinations"],
                line=dict(
                    color="Red",
                    width=1,
                    dash="dot"
                )
            )

            fig.add_shape(type="line",
                x0=country_info[c]["date"], y0=0, x1=country_info[c]["goal_date"], y1=0,
                line=dict(
                    color="Red",
                    width=1,
                    dash="dot",
                )
            )

            # fig.update_shapes(dict(xref='x', yref='y'))
            st.plotly_chart(fig, use_container_width=True)

    # @st.cache
    def process_vaccination_data(df_vaccination_data_raw, locations):
        df = df_vaccination_data_raw[df_vaccination_data_raw["location"].isin(locations)]
        
        df["daily_vaccinations_cumsum"] = df["daily_vaccinations"].groupby(df["location"]).transform("cumsum")

        df_grouped = df.groupby(["location"])

        country_info = df_grouped.agg(lambda x: x.iloc[-1]).to_dict("index")

        for c in country_info:
            country_info[c].update(**get_population(c, year))
            country_info[c]["vaccinated_people"] = country_info[c]["daily_vaccinations_cumsum"] / 2
            country_info[c]["goal_vaccinations"] = (country_info[c]["population"]*70/100) * 2
            country_info[c]["days_to_goal"] = int(((country_info[c]["population"]*70/100) - country_info[c]["vaccinated_people"]) / country_info[c]["daily_vaccinations"] * 2)
            country_info[c]["goal_date"] = country_info[c]["date"] + timedelta(days=country_info[c]["days_to_goal"])

        plot_data(df_grouped, country_info)

    with st.spinner(text="Processing... Please wait... Tip: you can zoom in on charts to better see the data and hover over the points to see some tooltips.") :
        process_vaccination_data(df_vaccination_data_raw, locations)