import os
from datetime import timedelta

import pandas as pd
import streamlit as st
from icalendar import Calendar, Event
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections
from streamlit_calendar import calendar

from config import index_params
from milvus_db_utils.search import search


def main(data_file: str) -> None:
    data = load_data(os.path.join("data", data_file))

    if "selected_movies" not in st.session_state:
        st.session_state["selected_movies"] = []

    ################
    # Search block #
    ################
    col_search_a, col_search_b = st.columns([1, 1])
    with col_search_a:
        title_search_term = st.text_input(
            "Search for a movie using terms in title", value="", key="title_search_term"
        )
    with col_search_b:
        description_search = st.text_input(
            "Search for a movie using natural description",
            value="",
            key="description_search",
        )
    show_selected = st.checkbox("Show Selected Only")

    ################
    # Save block   #
    ################
    if st.button("Save my movie selection"):
        selected_data = data.iloc[st.session_state.selected_movies, :]
        selected_data.to_csv("selected_movies.txt", index=False)
        create_ics_file(
            "program.ics",
            selected_data,
        )
        st.success("Movies saved successfully in selected_movies.txt and program.ics")

    #####################################
    # Display movies and program block  #
    #################@###################
    col_a, col_b = st.columns([4, 7])
    with col_a:
        filtered_data = filter_data(
            data, title_search_term, description_search, show_selected
        )
        selected_data = data.iloc[st.session_state.selected_movies, :]
        selected_data.to_csv("test.csv")
        show_selection(filtered_data)
    with col_b:
        show_calendar(
            data.iloc[st.session_state.selected_movies, :], data["Start"].min()
        )


@st.cache_data
def load_data(filename: str) -> pd.DataFrame:
    data = pd.read_csv(filename)
    data["StartDatetime"] = pd.to_datetime(data["StartDatetime"])
    data["EndDatetime"] = pd.to_datetime(data["EndDatetime"])
    return data


def filter_data(
    data: pd.DataFrame,
    title_search_term: str,
    description_search_term: str,
    show_selected: bool,
) -> pd.DataFrame:
    if show_selected:
        return data.iloc[st.session_state.selected_movies, :]
    elif title_search_term != "":
        return data[
            data["Title"].str.contains(title_search_term, case=False)
            | data["Description"].str.contains(title_search_term, case=False)
        ]
    else:
        index_param = index_params[0]
        collection_name = (
            f'embedded_field_{index_param["index_type"]}_'
            f'{index_param["metric_type"]}'
        )
        collection = Collection(name=collection_name)
        collection.load()
        print(index_param)
        results = search(description_search_term, index_param, collection)
        return data.iloc[[result[0] for result in results], :]


def show_selection(data: pd.DataFrame) -> None:
    for index, row in data.iterrows():
        is_selected = (
            st.session_state.selected_movies is not None
            and index in st.session_state.selected_movies
        )
        col1, col2 = st.columns([1, 2])
        col1.image(row["ImageURL"], use_column_width=True)
        col2.write(f'**{row["Title"]}**')
        col2.write(row["Description"])

        box = col1.checkbox("Select", key=index, value=is_selected)

        if box:
            if index not in st.session_state.selected_movies:
                st.session_state.selected_movies.append(index)
        else:
            if index in st.session_state.selected_movies:
                st.session_state.selected_movies.remove(index)


def test_delay(x: pd.Timedelta) -> str:
    if x is None:
        return "green"
    else:
        if x < pd.Timedelta(0):
            return "red"
        else:
            return "green"


def show_calendar(filtered_data: pd.DataFrame, initial_date: str) -> pd.DataFrame:
    data = filtered_data.copy()
    data = data.sort_values(by=["StartDatetime"])
    data.to_csv("test.csv", index=False)
    data["Delay"] = data["StartDatetime"] - data["EndDatetime"].shift(1)
    data["Color"] = data["Delay"].apply(test_delay)
    calendar_options = {
        "initialDate": initial_date,
        "slotMinTime": "06:00:00",
        "slotMaxTime": "24:00:00",
        "width": "100%",
    }
    calendar_events = []
    for index, row in data.iterrows():
        calendar_events.append(
            {
                "title": row["Title"],
                "color": row["Color"],
                "start": row["Start"],
                "end": row["End"],
            }
        )
    calendar_displayed = calendar(events=calendar_events, options=calendar_options)
    st.write(calendar_displayed)

    return data


def create_ics_file(file_name: str, selected_data: pd.DataFrame) -> None:
    events = []
    cal = Calendar()
    for _, row in selected_data.iterrows():
        events.append(
            {
                "title": row["Title"],
                "start": row["StartDatetime"],
                "duration": row["Duration"],
                "location": row["Location"],
            }
        )

    for event in events:
        ev = Event()
        ev.add("summary", event["title"])
        ev.add("dtstart", event["start"])
        ev.add("dtend", event["start"] + timedelta(minutes=event["duration"]))
        ev.add("location", event["location"])
        cal.add_component(ev)

    with open(file_name, "wb") as f:
        f.write(cal.to_ical())


if __name__ == "__main__":
    st.set_page_config(
        page_title="My Movie Festival App",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    css = """
    <style>
        section.main>div {
            padding-bottom: 1rem;
        }
        [data-testid="column"] {
            max-height: 70vh;
            max-width: 700vh;
            overflow: auto;
        }
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

    if "data_downloaded" not in st.session_state:
        st.session_state["data_downloaded"] = False

    data_source = st.selectbox("Choose your data source:", os.listdir("data"))

    if st.button("Confirm selection"):
        st.session_state["data_downloaded"] = True
    if st.session_state["data_downloaded"]:
        main(data_source)
