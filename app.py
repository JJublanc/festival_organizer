import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
from icalendar import Calendar, Event
from datetime import timedelta
import os


# TODO : add an area to write the name of the festival
# TODO : add a button to download icalendar and program.txt
# TODO : add a menu to select the data source (name of the csv used)
# TODO : add a button to launch the scrapping of the data source
# TODO : add an area to choose the year of the festival
# TODO : add a button to clear selection
# TODO : add a button to clear search

@st.cache_data
def load_data(filename):
	data = pd.read_csv(filename)
	data['StartDatetime'] = pd.to_datetime(data['StartDatetime'])
	data['EndDatetime'] = pd.to_datetime(data['EndDatetime'])
	return data


def filter_data(data, search_term, show_selected):
	if show_selected:
		return data.iloc[st.session_state.selected_movies, :]
	else:
		return data[data['Title'].str.contains(search_term, case=False) | data[
			'Description'].str.contains(search_term, case=False)]


def show_selection(data):
	for index, row in data.iterrows():
		is_selected = st.session_state.selected_movies is not None and index in st.session_state.selected_movies
		col1, col2 = st.columns([1, 2])
		col1.image(row['ImageURL'], use_column_width=True)
		col2.write(f'**{row["Title"]}**')
		col2.write(row['Description'])

		box = col1.checkbox('Select', key=index, value=is_selected)

		if box:
			if index not in st.session_state.selected_movies:
				st.session_state.selected_movies.append(index)
		else:
			if index in st.session_state.selected_movies:
				st.session_state.selected_movies.remove(index)


def test_delay(x):
	try:
		if x < pd.Timedelta(0):
			return 'red'
		else:
			return 'green'
	except:
		return 'green'


def show_calendar(filtered_data, initial_date):
	data = filtered_data.copy()
	data = data.sort_values(by=['StartDatetime'])
	data.to_csv("test.csv", index=False)
	data['Delay'] = data['StartDatetime'] - data['EndDatetime'].shift(1)
	data['Color'] = data['Delay'].apply(test_delay)
	calendar_options = {
		"initialDate": initial_date,
		"slotMinTime": "06:00:00",
		"slotMaxTime": "24:00:00",
		"width": "100%",
	}
	calendar_events = []
	for index, row in data.iterrows():
		calendar_events.append({
			"title": row['Title'],
			"color": row['Color'],
			"start": row['Start'],
			"end": row['End'],
		})
	calendar_displayed = calendar(events=calendar_events,
	                              options=calendar_options)
	st.write(calendar_displayed)

	return data


def create_ics_file(file_name, selected_data):
	events = []
	cal = Calendar()
	for _, row in selected_data.iterrows():
		events.append({
			'title': row['Title'],
			'start': row['StartDatetime'],
			'duration': row['Duration'],
			'location': row['Location']
		})

	for event in events:
		ev = Event()
		ev.add('summary', event['title'])
		ev.add('dtstart', event['start'])
		ev.add('dtend', event['start'] + timedelta(minutes=event['duration']))
		ev.add('location', event['location'])
		cal.add_component(ev)

	with open(file_name, 'wb') as f:
		f.write(cal.to_ical())


###
def main(data_file):
	data = load_data(os.path.join("data", data_file))

	if 'selected_movies' not in st.session_state:
		st.session_state['selected_movies'] = []

	if st.button('Save my movie selection'):
		selected_data = data.iloc[st.session_state.selected_movies, :]
		selected_data.to_csv(
			'selected_movies.txt', index=False)
		create_ics_file(
			"program.ics",
			selected_data,
		)
		print(selected_data)
		st.success(
			"Movies saved successfully in selected_movies.txt and program.ics")

	search_term = st.text_input("Search for a movie")
	show_selected = st.checkbox("Show Selected Only")

	colA, colB = st.columns([4, 7])
	with colA:
		filtered_data = filter_data(data, search_term, show_selected)
		selected_data = data.iloc[st.session_state.selected_movies, :]
		selected_data.to_csv("test.csv")
		show_selection(filtered_data)
	with colB:
		show_calendar(data.iloc[st.session_state.selected_movies, :],
		              data["Start"].min())


if __name__ == "__main__":
	st.set_page_config(
		page_title="My Movie Festival App",
		layout="wide",
		initial_sidebar_state="expanded",
	)

	css = '''
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
    '''

	st.markdown(css, unsafe_allow_html=True)

	data_source = st.selectbox(
		"Choose your data source:",
		os.listdir("data")
	)

	if 'data_downloaded' not in st.session_state:
		st.session_state['data_downloaded'] = False

	if st.button("Confirm selection"):
		st.session_state['data_downloaded'] = True
	if st.session_state['data_downloaded']:
		main(data_source)
