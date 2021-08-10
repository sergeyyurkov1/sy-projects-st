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
    import pycountry
    
    st.title("Vaccination Goal Visualizer")
    st.markdown("""
        This app approximates a date when our global vaccination goals will be achieved; data is updated every day and automatically reflected in charts.
        * **Data sources:** [Our World In Data](https://ourworldindata.org/covid-vaccinations), [United Nations](https://population.un.org/wpp)
        * **Disclaimer:** *work in progress; vaccination data in certain regions is reported inconsistently; plot figures are estimated and can not be fully accurate*
    """)
    st.markdown("*Due to some scaling issues, if viewing on mobile, please turn your device to landscape mode*")

    demographic_data = "https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/EXCEL_FILES/1_Population/WPP2019_POP_F01_1_TOTAL_POPULATION_BOTH_SEXES.xlsx"
    vaccination_data = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv"

    year = "2020"

    @st.cache(show_spinner=False)
    def get_vaccination_data() -> pd.DataFrame:
        df = pd.read_csv(vaccination_data, usecols=["date", "location", "daily_vaccinations"], parse_dates=["date"])
        return df

    @st.cache(show_spinner=False)
    def read_population_data():
        df = pd.read_excel(demographic_data)

        # Removes first 14 rows containing unrelated information
        df = df.iloc[15:]

        # Sets the first row as column names
        df.columns = df.iloc[0]

        # Removes the first row containing column names as it is no longer needed
        df = df.iloc[1:]

        return df

    # Selects country population
    # @st.cache(show_spinner=False)
    def get_population(country: str, year: str) -> dict:
        df1 = read_population_data()
        population = {}
        try:
            code_obj = pycountry.countries.search_fuzzy(country)[0]
            code = int(code_obj.numeric)
            population["population"] = df1.loc[ df1[df1.columns[4]] == code, year ].values[0] * 1000
            # population["population"] = df1.loc[ df1[df1.columns[2]].str.contains(country), year ].values[0] * 1000
        # except (LookupError, OutOfBoundsDatetime) as e:
        except:
            st.error(f"Something went wrong when looking up data for {country}. Please select a different location. I am working on a solution.")
            st.stop()
        
        return population
    
    ##############################
    # Vaccination data
    ##############################
    with st.spinner(text="Loading vaccination data...") :
        df_vaccination_data_raw = get_vaccination_data()

    sorted_unique_locations = sorted(df_vaccination_data_raw.location.unique())

    locations = st.multiselect("Select location(s)", sorted_unique_locations)

    ##############################
    # Functions
    ##############################
    @st.cache(show_spinner=False)
    def make_plot(df, country_info, l, year):
        
        country = df

        # Annotations to display
        days_to_goal = int(country_info[l]["days_to_goal"])
        goal_vaccinations = int(country_info[l]["goal_vaccinations"])
        population = int(country_info[l]["population"])
        date = country_info[l]["date"]
        daily_vaccinations = int(country_info[l]["daily_vaccinations"])
        vaccinated_people = int(country_info[l]["vaccinated_people"])
        goal_date = country_info[l]["goal_date"]

        vacc_start_date = country.iloc[0,0]

        # ---------------------------------------------------------------------------------------------------------

        fig = go.Figure()

        fig.add_trace(go.Bar(x=country["date"], y=country["daily_vaccinations_cumsum"],
            name="shots",
            yaxis="y1",)
        )

        fig.add_trace(go.Line(x=country["date"], y=country["daily_vaccinations"], yaxis="y2", name="shots"))

        fig.update_layout(
            xaxis=dict(
                title="<b>Days</b>",
                showgrid=False,
            ),
            yaxis=dict(
                title="<b>Vaccinations done,</b> shots (cumulative sum)",
                # titlefont=dict(
                #     color="#1f77b4"
                # ),
                # tickfont=dict(
                #     color="#1f77b4"
                # ),
                showgrid=False,
                anchor = 'x',
                rangemode="tozero",
            ),
            yaxis2=dict(
                title="<b>Daily vaccinations,</b> shots",
                # titlefont=dict(
                #     color="#1f77b4"
                # ),
                # tickfont=dict(
                #     color="#1f77b4"
                # ),
                anchor="x",
                overlaying="y",
                side="right",
                showgrid=False,
                rangemode="nonnegative",
                scaleanchor = "y1",
                scaleratio=10,
            ),
        )

        fig.update_traces(marker_color="#9481d2", hovertemplate="%{y:,}")

        text = f"<b>Vaccination goal</b><br>70% / 2 doses<br>in <b>{days_to_goal} days ({goal_date:%B %Y})</b><br>~ {humanize.intword(goal_vaccinations)} doses required"
        font_color = "Orange"
        color="Orange"
        if days_to_goal <= 0:
            text = f"<b>Vaccination goal</b><br>70% / 2 doses<br>is <b>achieved</b>"
            font_color = "Green"
            color="Green"

        fig.add_annotation(
            text=text,
            align="left",
            x=country_info[l]["goal_date"],
            y=country_info[l]["goal_vaccinations"],
            font_color=font_color,
            # arrowcolor="Red",
            # arrowhead=1,
            # hovertext=f"~ {humanize.intword(goal_vaccinations)} doses required",
            showarrow=False,
            # yanchor="top",
            xanchor="left",
            xshift=10,
            bgcolor="rgba(255,255,255,0.85)"
        )

        fig.add_annotation(
            text=f"<b>Population:</b> {population:,} ({year})<br><b>Vaccination started:</b> {vacc_start_date:%B %d, %Y}<br><b>{date:%B %d, %Y}:</b> {vaccinated_people:,} ({int(vaccinated_people*100/population)}%) people<br>received at least 2 doses of vaccine,<br>{daily_vaccinations:,} shots were administered",
            align="left",
            x=0.05,
            y=0.95,
            xref="paper", yref="paper",
            # hovertext=f"",
            showarrow=False,
            # xanchor="right",
            # xshift=-10,
            # bgcolor="rgba(169,169,169,0.35)"
        )

        # Vertical line
        # -------------
        fig.add_shape(type="line",
            x0=country_info[l]["goal_date"], y0=0, x1=country_info[l]["goal_date"], y1=country_info[l]["goal_vaccinations"],
            line=dict(
                color="White",
                width=2,
                # dash="dot"
            )
        )
        fig.add_shape(type="line",
            x0=country_info[l]["goal_date"], y0=0, x1=country_info[l]["goal_date"], y1=country_info[l]["goal_vaccinations"],
            line=dict(
                color=color,
                width=2,
                dash="dot"
            )
        )

        # fig.add_annotation(text=f"<b>Population:</b> {population:,} ({year})<br><b>Vaccination started:</b> {vacc_start_date:%B %d, %Y}<br><b>{date:%B %d, %Y}:</b> {vaccinated_people:,} ({int(vaccinated_people*100/population)}%) people received at least 2 doses of vaccine,<br>{daily_vaccinations:,} shots were administered",
        #     align="left",
        #     xref="paper", yref="paper",
        #     x=0.1, y=0.9,
        #     showarrow=False,
        #     bgcolor="rgba(169,169,169,0.35)"
        # )

        

        fig.update_layout({
            "plot_bgcolor": "#f5f7f3",
            "paper_bgcolor": "#f5f7f3"}, hovermode="x", hoverlabel=dict(font_color="white"),
        )

        fig.update_layout(
            title_text=f"{l}",
            width=800,
            showlegend=False,
        )

        return fig

    @st.cache(show_spinner=False, suppress_st_warning=True)
    def process_vaccination_data(df_vaccination_data_raw, l):

        # df = df_vaccination_data_raw[df_vaccination_data_raw["location"].isin(l)]
        df = df_vaccination_data_raw[df_vaccination_data_raw["location"] == l]
        
        # df["daily_vaccinations_cumsum"] = df["daily_vaccinations"].groupby(df["location"]).transform("cumsum")
        df["daily_vaccinations_cumsum"] = df["daily_vaccinations"].transform("cumsum")

        # df_grouped = df.groupby(["location"])

        # country_info = df_grouped.agg(lambda x: x.iloc[-1]).to_dict("index")

        df.set_index("location", inplace=True, drop=True)

        country_info_series = df.iloc[-1]
        country_info = {country_info_series.name: dict(country_info_series)}

        country_info[l].update(**get_population(l, year))
        country_info[l]["vaccinated_people"] = country_info[l]["daily_vaccinations_cumsum"] / 2
        country_info[l]["goal_vaccinations"] = (country_info[l]["population"]*70/100) * 2
        country_info[l]["days_to_goal"] = int(((country_info[l]["population"]*70/100) - country_info[l]["vaccinated_people"]) / country_info[l]["daily_vaccinations"] * 2)
        country_info[l]["goal_date"] = country_info[l]["date"] + timedelta(days=country_info[l]["days_to_goal"])

        return df, country_info

    with st.spinner(text="Tip: you can zoom in on charts to better see the data.") :
        for l in locations:
            df, country_info = process_vaccination_data(df_vaccination_data_raw, l)

            fig = make_plot(df, country_info, l, year)
            st.plotly_chart(fig, use_container_width=True)