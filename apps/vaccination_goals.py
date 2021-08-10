from os import X_OK
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
            if country != "World":
                code_obj = pycountry.countries.search_fuzzy(country)[0]
                code = int(code_obj.numeric)
                population["population"] = df1.loc[ df1[df1.columns[4]] == code, year ].values[0] * 1000
            else:
                # population["population"] = df1.loc[ df1[df1.columns[2]] == country.toupper(), year ].values[0] * 1000
                population["population"] = df1.loc[ df1[df1.columns[2]].str.contains(country.toupper()), year ].values[0] * 1000
        # except (LookupError, OutOfBoundsDatetime) as e:
        except Exception as e:
            print(e)
            # st.error(f"Something went wrong when looking up data for {country}. Please select a different location. I am working on a solution.")
            # st.stop()
        
        return population
    
    ##############################
    # Vaccination data
    ##############################
    with st.spinner(text="Loading vaccination data...") :
        df_vaccination_data_raw = get_vaccination_data()

    sorted_unique_locations = sorted(df_vaccination_data_raw.location.unique())

    locations = st.multiselect("Select location(s)", sorted_unique_locations)
    #default="World"

    ##############################
    # Functions
    ##############################
    @st.cache(show_spinner=False)
    def make_plot(df, location_info, location, year):
        # Annotations to display
        days_to_goal = int(location_info[location]["days_to_goal"])
        goal_vaccinations = int(location_info[location]["goal_vaccinations"])
        population = int(location_info[location]["population"])
        date = location_info[location]["date"]
        daily_vaccinations = int(location_info[location]["daily_vaccinations"])
        vaccinated_people = int(location_info[location]["vaccinated_people"])
        goal_date = location_info[location]["goal_date"]

        vacc_start_date = df.iloc[0,0]

        df["percent_fully_vaccinated"].fillna(0, inplace=True)
        df = df.astype({"percent_fully_vaccinated": int})

        try:
            date_vacc_50_perc = df.loc[df["percent_fully_vaccinated"] == 50, "date"][-1]
            daily_vaccinations_cumsum_50_perc = df.loc[df["percent_fully_vaccinated"] == 50, "daily_vaccinations_cumsum"][-1]
        except IndexError:
            date_vacc_50_perc = location_info[location]["goal_date_50_perc"]
            daily_vaccinations_cumsum_50_perc = location_info[location]["goal_vaccinations_50_perc"]

        try:
            date_vacc_30_perc = df.loc[df["percent_fully_vaccinated"] == 30, "date"][-1]
            daily_vaccinations_cumsum_30_perc = df.loc[df["percent_fully_vaccinated"] == 30, "daily_vaccinations_cumsum"][-1]
        except IndexError:
            date_vacc_30_perc = location_info[location]["goal_date_30_perc"]
            daily_vaccinations_cumsum_30_perc = location_info[location]["goal_vaccinations_30_perc"]



        # ---------------------------------------------------------------------------------------------------------

        fig = go.Figure()

        fig.add_trace(go.Bar(x=df["date"], y=df["daily_vaccinations_cumsum"],
            name="shots",
            yaxis="y1",)
        )

        fig.add_trace(go.Line(x=df["date"], y=df["daily_vaccinations"], yaxis="y2", name="shots"))

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

        fig.update_traces(marker_color="rgba(148, 129, 210, 0.5)",
            marker_line_width = 0,
            selector=dict(type="bar"),
            hovertemplate="%{y:,}",
        )

        fig.update_traces(marker_color="Red",
            # marker_line_width = 0,
            selector=dict(type="line"),
            hovertemplate="%{y:,}",
        )

        text = f"<b>Vaccination Goal</b><br>70% and 2 doses<br>in <b>{days_to_goal} days ({goal_date:%B %Y})</b><br>~ {humanize.intword(goal_vaccinations)} doses required"
        font_color = "Orange"
        color="Orange"
        if days_to_goal <= 0:
            text = f"<b>Vaccination goal</b><br>70% / 2 doses<br>is <b>achieved</b>"
            font_color = "Green"
            color="Green"

        fig.add_annotation(
            text=text,
            align="left",
            x=location_info[location]["goal_date"],
            y=location_info[location]["goal_vaccinations"],
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

        # def add_goal_marker(perc: int):


        # Vertical line 70%
        # -------------
        fig.add_shape(type="line",
            x0=location_info[location]["goal_date"], y0=0, x1=location_info[location]["goal_date"], y1=location_info[location]["goal_vaccinations"],
            line=dict(
                color="White",
                width=2,
                # dash="dot"
            )
        )
        fig.add_shape(type="line",
            x0=location_info[location]["goal_date"], y0=0, x1=location_info[location]["goal_date"], y1=location_info[location]["goal_vaccinations"],
            line=dict(
                color=color,
                width=2,
                dash="dot"
            )
        )
        # -------------

        # Vertical line 50%
        # -------------
        text_50_perc = "<b>50%</b>"
        font_color_50_perc = "Orange"
        color_50_perc="Orange"
        if int(location_info[location]["days_to_goal_50_perc"]) <= 0:
            text_50_perc = f"<b>50% reached</b>"
            font_color_50_perc = "Green"
            color_50_perc="Green"
        fig.add_annotation(
            text=text_50_perc,
            align="left",
            x=date_vacc_50_perc,
            y=daily_vaccinations_cumsum_50_perc,
            font_color=font_color_50_perc,
            # arrowcolor="Red",
            # arrowhead=1,
            # hovertext=f"~ {humanize.intword(goal_vaccinations)} doses required",
            showarrow=False,
            yanchor="bottom",
            # xanchor="left",
            # xshift=10,
            bgcolor="rgba(255,255,255,0.85)"
        )
        fig.add_shape(type="line",
            x0=date_vacc_50_perc, y0=0, x1=date_vacc_50_perc, y1=daily_vaccinations_cumsum_50_perc,
            line=dict(
                color="White",
                width=2,
                # dash="dot"
            )
        )
        fig.add_shape(type="line",
            x0=date_vacc_50_perc, y0=0, x1=date_vacc_50_perc, y1=daily_vaccinations_cumsum_50_perc,
            line=dict(
                color=color,
                width=2,
                dash="dot"
            )
        )
        # -------------

        # Vertical line 30%
        # -------------
        text_30_perc = "<b>30%</b>"
        font_color_30_perc = "Orange"
        color_30_perc="Orange"
        if int(location_info[location]["days_to_goal_30_perc"]) <= 0:
            text_30_perc = f"<b>30% reached</b>"
            font_color_30_perc = "Green"
            color_30_perc="Green"
        fig.add_annotation(
            text=text_30_perc,
            align="left",
            x=date_vacc_30_perc,
            y=daily_vaccinations_cumsum_30_perc,
            font_color=font_color_30_perc,
            # arrowcolor="Red",
            # arrowhead=1,
            # hovertext=f"~ {humanize.intword(goal_vaccinations)} doses required",
            showarrow=False,
            yanchor="bottom",
            # xanchor="left",
            # xshift=10,
            bgcolor="rgba(255,255,255,0.85)"
        )
        
        fig.add_shape(type="line",
            x0=date_vacc_30_perc, y0=0, x1=date_vacc_30_perc, y1=daily_vaccinations_cumsum_30_perc,
            line=dict(
                color="White",
                width=2,
                # dash="dot"
            )
        )

        fig.add_shape(type="line",
            x0=date_vacc_30_perc, y0=0, x1=date_vacc_30_perc, y1=daily_vaccinations_cumsum_30_perc,
            line=dict(
                color=color,
                width=2,
                dash="dot"
            )
        )

        fig.update_layout({
            "plot_bgcolor": "#f5f7f3",
            "paper_bgcolor": "#f5f7f3"}, hovermode="x", hoverlabel=dict(font_color="white"),
        )

        fig.update_layout(
            title_text=f"{location}",
            width=800,
            showlegend=False,
        )

        return fig

    # ---------------------------------------------------------------------------------------------------------
    @st.cache(show_spinner=False, suppress_st_warning=True)
    def process_vaccination_data(df_vaccination_data_raw, location):

        df = df_vaccination_data_raw[df_vaccination_data_raw["location"] == location]
        
        df["daily_vaccinations_cumsum"] = df["daily_vaccinations"].transform("cumsum")

        df.set_index("location", inplace=True, drop=True)

        location_info_series = df.iloc[-1]
        location_info = {location_info_series.name: dict(location_info_series)}

        location_info[location].update(**get_population(location, year))

        location_info[location]["vaccinated_people"] = location_info[location]["daily_vaccinations_cumsum"] / 2

        df["percent_fully_vaccinated"] = df["daily_vaccinations_cumsum"].apply(lambda x: (x*100)/(location_info[location]["population"]*2))

        # Predictions
        # -----------
        # 70%
        location_info[location]["goal_vaccinations"] = (location_info[location]["population"]*70/100) * 2
        location_info[location]["days_to_goal"] = int(((location_info[location]["population"]*70/100) - location_info[location]["vaccinated_people"]) / location_info[location]["daily_vaccinations"] * 2)
        location_info[location]["goal_date"] = location_info[location]["date"] + timedelta(days=location_info[location]["days_to_goal"])

        # 50%
        location_info[location]["goal_vaccinations_50_perc"] = (location_info[location]["population"]*50/100) * 2
        location_info[location]["days_to_goal_50_perc"] = int(((location_info[location]["population"]*50/100) - location_info[location]["vaccinated_people"]) / location_info[location]["daily_vaccinations"] * 2)
        location_info[location]["goal_date_50_perc"] = location_info[location]["date"] + timedelta(days=location_info[location]["days_to_goal_50_perc"])

        # 30%
        location_info[location]["goal_vaccinations_30_perc"] = (location_info[location]["population"]*30/100) * 2
        
        location_info[location]["days_to_goal_30_perc"] = int(((location_info[location]["population"]*30/100) - location_info[location]["vaccinated_people"]) / location_info[location]["daily_vaccinations"] * 2)

        location_info[location]["goal_date_30_perc"] = location_info[location]["date"] + timedelta(days=location_info[location]["days_to_goal_30_perc"])

        return df, location_info

    with st.spinner(text="Tip: you can zoom in on charts to better see the data.") :
        for location in locations:
            breakpoint()
            df, location_info = process_vaccination_data(df_vaccination_data_raw, location)
            
            fig = make_plot(df, location_info, location, year)
            st.plotly_chart(fig, use_container_width=True)