import streamlit as st
import streamlit.components.v1 as components

import copy

import base64
from io import StringIO

import json

VERSION = 4.2

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

    st.title(f"Vaccination Goal Visualizer, v{VERSION}")
    st.markdown(
        """
        This app approximates a date when our global vaccination goals will be achieved given the current rate of vaccination; data are updated every day and automatically reflected in charts.
        * **Data sources:** [Our World In Data](https://ourworldindata.org/covid-vaccinations), [United Nations](https://population.un.org/wpp)
        * **Disclaimer:** *work in progress; vaccination data in certain regions is reported inconsistently; plot figures are estimated and can not be fully accurate*
        * Another excellent project using the same data from OWID: [Covidvax.live](https://covidvax.live/)
    """
    )

    demographic_data = "https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/EXCEL_FILES/1_Population/WPP2019_POP_F01_1_TOTAL_POPULATION_BOTH_SEXES.xlsx"
    vaccination_data = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv"

    year = "2020"

    @st.cache(show_spinner=False)
    def get_vaccination_data() -> pd.DataFrame:
        df = pd.read_csv(
            vaccination_data,
            usecols=["date", "location", "daily_vaccinations"],
            parse_dates=["date"],
        )
        return df

    @st.cache(show_spinner=False, suppress_st_warning=True)
    def read_population_data():
        import pickle
        try:
            with open("apps/data/population_data.pickle", "rb") as f:
                df = pickle.load(f)
        except FileNotFoundError:
            try:
                df = pd.read_excel(demographic_data)
                with open("apps/data/population_data.pickle", "wb") as f:
                    pickle.dump(df, f)
            except ValueError:
                st.warning("This app is currently unavailable due to a maintenance")
                st.stop()

        # Removes first 14 rows containing unrelated information
        df = df.iloc[15:]

        # Sets the first row as column names
        df.columns = df.iloc[0]

        # Removes the first row containing column names as it is no longer needed
        df = df.iloc[1:]

        return df

    location_codes = {
        "World": 900,
        "Asia": 935,
        "Cape Verde": 132,
        "Europe": 908,
        "High income": 1503,
        "Low income": 1500,
        "Upper middle income": 1502,
        "South Korea": 410,
        "South America": 931,
        "Oceania": 909,
        "North America": 905,
    }

    # TODO: needs a better algorithm
    # Commented out values have been fixed
    problematic_locations = [
        "Bonaire Sint Eustatius and Saba",
        "Burkina Faso",
        "Cook Islands",
        "Democratic Republic of Congo",
        "European Union",
        "Faeroe Islands",
        "Guernsey",
        "Uganda",
        "Turkmenistan",
        "Tanzania",
        "Sudan",
        "South Sudan",
        "Sao Tome and Principe",
        "Pitcairn",
        "Northern Cyprus",
        "Nigeria",
        "Niger",
    ]
    # "Falkland Islands"
    # "Bhutan"

    # Selects country population
    # @st.cache(show_spinner=False)
    def get_population(country: str, year: str) -> dict:
        population = {}

        df1 = read_population_data()

        try:
            if country in list(location_codes.keys()):
                code = location_codes[country]
            else:
                code_obj = pycountry.countries.search_fuzzy(country)[0]
                code = int(code_obj.numeric)
                # population["population"] = df1.loc[ df1[df1.columns[2]] == country.toupper(), year ].values[0] * 1000
                # population["population"] = df1.loc[ df1[df1.columns[2]].str.contains(country.toupper()), year ].values[0] * 1000
            population["population"] = (
                df1.loc[df1[df1.columns[4]] == code, year].values[0] * 1000
            )
        # except (LookupError, OutOfBoundsDatetime) as e:
        except Exception as e:
            # print(e)
            st.error(
                f"Something went wrong when looking up data for {country}. Please select a different location. I am working on a solution."
            )
            st.stop()

        return population

    ##############################
    # Functions
    ##############################
    @st.cache(show_spinner=False, allow_output_mutation=True)
    def make_plot(df1, location_info1, location, year):
        df = copy.deepcopy(df1)
        location_info = copy.deepcopy(location_info1)

        df = df.astype({"percent_fully_vaccinated": int})

        def set_predict_or_fact(perc: int) -> None:
            def closest(lst, K):
                return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - K))]

            percent_fully_vaccinated_list = df["percent_fully_vaccinated"].tolist()

            perc_approx = closest(percent_fully_vaccinated_list, perc)

            if (
                perc - perc_approx > np.diff(percent_fully_vaccinated_list).max()
                or perc_approx - perc < -np.diff(percent_fully_vaccinated_list).max()
            ):
                perc_approx = perc

            try:  #
                location_info[location][f"date_vacc_{perc}_perc"] = df.loc[
                    df["percent_fully_vaccinated"] == perc_approx, "date"
                ][-1]
                location_info[location][
                    f"daily_vaccinations_cumsum_{perc}_perc"
                ] = df.loc[
                    df["percent_fully_vaccinated"] == perc_approx,
                    "daily_vaccinations_cumsum",
                ][
                    -1
                ]
            except IndexError:
                location_info[location][f"date_vacc_{perc}_perc"] = location_info[
                    location
                ][f"goal_date_{perc}_perc"]
                location_info[location][
                    f"daily_vaccinations_cumsum_{perc}_perc"
                ] = location_info[location][f"goal_vaccinations_{perc}_perc"]
            return None

        set_predict_or_fact(10)
        set_predict_or_fact(30)
        set_predict_or_fact(50)
        set_predict_or_fact(70)
        set_predict_or_fact(80)
        set_predict_or_fact(100)

        # ---------------------------------------------------------------------------------------------------------

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=df["date"],
                y=df["daily_vaccinations_cumsum"],
                name="total",
                hoverinfo="y",
                hovertemplate="%{y:,}",
                yaxis="y1",
            )
        )

        fig.add_trace(
            go.Line(
                x=df["date"],
                y=df["daily_vaccinations"],
                name="daily",
                hoverinfo="y",
                hovertemplate="%{y:,}",
                yaxis="y2",
            )
        )

        fig.update_layout(
            xaxis=dict(
                title="<b>Days</b>",
                showgrid=False,
            ),
            yaxis=dict(
                title="<b>Total vaccinations,</b> shots (cumulative daily sum)",
                # titlefont=dict(
                #     color="#1f77b4"
                # ),
                # tickfont=dict(
                #     color="#1f77b4"
                # ),
                showgrid=False,
                anchor="x",
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
                overlaying="y1",
                side="right",
                showgrid=False,
                rangemode="nonnegative",
                scaleanchor="y1",
                scaleratio=50,
            ),
        )

        fig.update_traces(
            marker_color="rgba(148, 129, 210, 0.7)",
            marker_line_width=0,
            selector=dict(type="bar"),
        )

        fig.update_traces(
            marker_color="Red",
            marker_line_width=0,
            selector=dict(type="line"),
        )

        # ---------------------------------------------------------------------------------------------------------------------------

        _population = int(location_info[location]["population"])
        _vacc_start_date = location_info[location]["vacc_start_date"]
        _date = location_info[location]["date"]
        _vaccinated_people = int(location_info[location]["vaccinated_people"])
        _daily_vaccinations = location_info[location]["daily_vaccinations"]

        fig.add_annotation(
            text=f"<b>Population:</b> {humanize.intword(_population)} ({year})<br><b>Vaccination started:</b> {_vacc_start_date:%B %d, %Y}<br><b>{_date:%B %d, %Y}:</b> {_vaccinated_people:,} ({int(_vaccinated_people*100/int(_population))}%) people<br>have received at least 2 doses of vaccine,<br>{int(_daily_vaccinations):,} shots were administered",
            align="left",
            x=0.05,
            y=0.95,
            xref="paper",
            yref="paper",
            # hovertext=f"",
            showarrow=False,
            # xanchor="right",
            # xshift=-10,
            # bgcolor="rgba(169,169,169,0.35)"
        )

        # ---------------------------------------------------------------------------------------------------------------------------

        def add_goal_marker(
            perc: int, xanchor: str, xshift: int, text: str = None
        ) -> None:
            xanchor = xanchor
            xshift = xshift
            if int(location_info[location][f"days_to_goal_{perc}_perc"]) <= 0:
                text = f"<b>{perc}%</b>"
                font_color = "Green"
                color = "Green"
                xanchor = "right"
                xshift = 5
            else:
                text = text or f"<b>{perc}%</b>"
                font_color = "Orange"
                color = "Orange"
            fig.add_annotation(
                text=text,
                align="center",
                x=location_info[location][f"date_vacc_{perc}_perc"],
                y=location_info[location][f"daily_vaccinations_cumsum_{perc}_perc"],
                font_color=font_color,
                # arrowcolor="Red",
                # arrowhead=1,
                # hovertext=f"",
                showarrow=False,
                yanchor="bottom",
                xanchor=xanchor,
                xshift=xshift,
                bgcolor="rgba(255,255,255,0.85)",
            )
            fig.add_shape(
                type="line",
                x0=location_info[location][f"date_vacc_{perc}_perc"],
                y0=0,
                x1=location_info[location][f"date_vacc_{perc}_perc"],
                y1=location_info[location][f"daily_vaccinations_cumsum_{perc}_perc"],
                line=dict(
                    color="White",
                    width=2,
                    # dash="dot"
                ),
            )
            fig.add_shape(
                type="line",
                x0=location_info[location][f"date_vacc_{perc}_perc"],
                y0=0,
                x1=location_info[location][f"date_vacc_{perc}_perc"],
                y1=location_info[location][f"daily_vaccinations_cumsum_{perc}_perc"],
                line=dict(color=color, width=2, dash="dot"),
            )
            return None

        # humanize.naturalday(dt.datetime.now() - dt.timedelta(days=1))

        def get_annotation_for_goal_marker(perc: int) -> str:
            return "<b>-- {_perc}% --</b><br>in <b>{_days_to_goal} day(s)</b><br><b>({_goal_date:%B %Y})</b><br>~ {_goal_vaccinations} doses".format(
                _perc = perc,
                _days_to_goal=int(location_info[location][f"days_to_goal_{perc}_perc"]),
                _goal_date=location_info[location][f"goal_date_{perc}_perc"],
                _goal_vaccinations=humanize.intword(
                    int(location_info[location][f"goal_vaccinations_{perc}_perc"])
            ),
        )

        add_goal_marker(10, "right", 5)
        add_goal_marker(30, "right", 5)
        add_goal_marker(50, "right", 5)
        add_goal_marker(70, "right", 5)  # , get_annotation_for_goal_marker(70)
        add_goal_marker(80, "left", -5, get_annotation_for_goal_marker(80))
        add_goal_marker(100, "left", -5, get_annotation_for_goal_marker(100))

        fig.update_layout(
            {"plot_bgcolor": "#f5f7f3", "paper_bgcolor": "#f5f7f3"},
            hovermode="x",
            hoverlabel=dict(font_color="white"),
            title_text=f"{location}",
            width=800,
            showlegend=False,
        )

        # fig.update_xaxes(ticklabelmode="period")

        return fig

    # ---------------------------------------------------------------------------------------------------------------------------
    # @st.cache(show_spinner=False, suppress_st_warning=True)
    # allow_output_mutation=True
    def process_vaccination_data(df_vaccination_data_raw, location):

        df = df_vaccination_data_raw[df_vaccination_data_raw["location"] == location]

        df["daily_vaccinations_cumsum"] = df["daily_vaccinations"].transform("cumsum")

        df.set_index("location", inplace=True, drop=True)

        location_info_series = df.iloc[-1]

        if location in problematic_locations:
            st.error(
                f"Sorry, cannot make a chart for {location}. Here is the raw data instead."
            )
            st.dataframe(df)
            st.stop()

        # ---------------------------------------------------------------------------------------------------------------------------

        location_info = {location_info_series.name: dict(location_info_series)}

        # ---------------------------------------------------------------------------------------------------------------------------

        location_info[location].update(**get_population(location, year))

        location_info[location]["vacc_start_date"] = df.iloc[0, 0]

        location_info[location]["vaccinated_people"] = (
            location_info[location]["daily_vaccinations_cumsum"] / 2
        )

        df["percent_fully_vaccinated"] = df["daily_vaccinations_cumsum"].apply(
            lambda x: (x * 100) / (location_info[location]["population"] * 2)
        )

        def set_predict_goal_date(perc: int) -> None:
            location_info[location][f"goal_vaccinations_{perc}_perc"] = (
                location_info[location]["population"] * perc / 100
            ) * 2
            location_info[location][f"days_to_goal_{perc}_perc"] = int(
                (
                    (location_info[location]["population"] * perc / 100)
                    - location_info[location]["vaccinated_people"]
                )
                / location_info[location]["daily_vaccinations"]
                * 2
            )
            location_info[location][f"goal_date_{perc}_perc"] = location_info[location][
                "date"
            ] + timedelta(days=location_info[location][f"days_to_goal_{perc}_perc"])
            return None

        set_predict_goal_date(10)
        set_predict_goal_date(100)
        set_predict_goal_date(80)
        set_predict_goal_date(70)
        set_predict_goal_date(50)
        set_predict_goal_date(30)

        df["percent_fully_vaccinated"].fillna(0, inplace=True)
        # df = df.astype({"percent_fully_vaccinated": int})

        return df, location_info

    ##############################
    # Entry point
    ##############################
    with st.spinner(text="Loading vaccination data..."):
        try:
            df_vaccination_data_raw = get_vaccination_data()
        except:
            st.error(f"Something went wrong. Please try again later.")
            st.stop()

    sorted_unique_locations = sorted(df_vaccination_data_raw.location.unique())

    locations = st.multiselect(
        "Select location(s)", sorted_unique_locations, default="World"
    )
    # default="World"

    with st.spinner(
        text="Tip: you can zoom in on and pan the chart, select areas, drag the axes and more..."
    ):
        for location in locations:
            df, location_info = process_vaccination_data(
                df_vaccination_data_raw, location
            )

            fig = make_plot(df, location_info, location, year)
            st.plotly_chart(fig, use_container_width=False)

            df.reset_index(drop=True, inplace=True)

            # if st.button(label="Show Dataset", key=location):
            with st.expander(label="Show/Hide Dataset", expanded=False):
                st.markdown(
                    """Missing data is indicated with <span style='font-weight:bold;'>nan</span>, <span style='background-color:#ffff00'>duplicate values</span> in <b>daily_vaccinations</b> are the result of missing data, last valid observations were used to fill the gap (forward fill)""",
                    unsafe_allow_html=True,
                )  # <span style='color:#ff0000; font-weight:bold;'>

                daily_vaccinations_duplicates = df["daily_vaccinations"].duplicated(
                    keep=False
                )
                daily_vaccinations_duplicate_rows = daily_vaccinations_duplicates[
                    daily_vaccinations_duplicates
                ].index.values
                st.dataframe(
                    df.style.apply(
                        lambda x: [
                            "background: yellow"
                            if x.name in daily_vaccinations_duplicate_rows
                            else ""
                            for i in x
                        ],
                        axis=1,
                        subset="daily_vaccinations",
                    )
                )

                # st.json(json.dumps(location_info, default=str))

                output = StringIO()
                df.to_csv(output)
                out = output.getvalue()
                b64 = base64.b64encode(
                    out.encode()
                ).decode()  # strings <-> bytes conversions is necessary here
                href = f'<a href="data:file/csv;base64,{b64}" download="Vaccination Info - {location}.csv">Download CSV</a>'
                st.markdown(href, unsafe_allow_html=True)
                output.close()
