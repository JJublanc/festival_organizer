import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
from datetime import datetime


def get_absolute_url(base_url, relative_url):
	# Combine the base URL with the relative URL to get the absolute URL
	return urljoin(base_url, relative_url)


def get_urls_from_div(url, div_class):
	try:
		# Make an HTTP GET request to the URL
		response = requests.get(url)

		# Check if the request was successful
		response.raise_for_status()

		# Parse the HTML content using BeautifulSoup
		soup = BeautifulSoup(response.content, 'html.parser')

		# Find all div elements with the given class
		div_elements = soup.find_all('div', class_=div_class)

		# Initialize a list to store all the URLs
		urls = []

		# Loop through each div element
		for div in div_elements:
			# Find all anchor elements within the div
			anchor_elements = div.find_all('a')
			for anchor in anchor_elements:
				# Get the 'href' attribute of the anchor element (i.e., the relative URL)
				relative_url = anchor.get('href')
				if relative_url:
					# Convert the relative URL to absolute URL
					absolute_url = get_absolute_url(url, relative_url)
					urls.append(absolute_url)


		return urls

	except requests.exceptions.RequestException as e:
		print("Error making the request:", e)
		return []


def get_info_from_session_url(url):
	try:
		# Make an HTTP GET request to the URL
		response = requests.get(url)

		# Check if the request was successful
		response.raise_for_status()

		# Parse the HTML content using BeautifulSoup
		soup = BeautifulSoup(response.content, 'html.parser')
		title = ""
		duration = 0
		absolute_image_url = ""

		# TITLE
		title_element = soup.find('h2', class_='content_details_title')
		if title_element:
			title = title_element.get_text().strip()

		# DURATION
		# Find the ul element with the class 'list-unstyled details_movie_basic'
		ul_elements = soup.find_all('ul',
		                            class_='list-unstyled details_movie_basic')
		for ul_element in ul_elements:
			duration_elements = ul_element.find_all('li')
			if duration_elements:
				for duration_element in duration_elements:
					duration += convert_duration_to_minutes(
						duration_element.text)

		img_element = soup.find('div', class_='details_main_picture').find('img')
		if img_element:
			image_url = img_element.get('src')
			if image_url:
				# Convert the relative URL to absolute URL
				absolute_image_url = get_absolute_url(url, image_url)

		# DATE, TIME, LOCATION
		seances = {}
		div = soup.find('div', class_="details_screenings")
		strong_element = div.find_all('strong')
		details_elements = soup.find_all('p', )
		for details_element in details_elements:
			# Get the text of the paragraph
			paragraph_text = details_element.get_text().strip()
			# Extract date, time, and location from the paragraph text
			date, time, location = extract_date_time_location(paragraph_text)
			if date:
				seances[date] = {'time': time, 'location': location}

		return title, duration, seances, absolute_image_url

	except requests.exceptions.RequestException as e:
		print("Error making the request:", e)


def convert_duration_to_minutes(duration_text):
	# Define regular expressions for matching hours and minutes
	hour_regex = r'(\d+)h'
	minute_regex = r'(\d+)mn|\d+m'

	# Initialize variables for hours and minutes
	hours = 0
	minutes = 0

	# Find hours in the duration text
	hour_match = re.search(hour_regex, duration_text)
	if hour_match:
		hours = int(hour_match.group(1))

	# Find minutes in the duration text
	minute_match = re.search(minute_regex, duration_text)
	if minute_match:
		minutes = int(minute_match.group(1))

	# Calculate the total duration in minutes
	total_minutes = hours * 60 + minutes

	return total_minutes


def extract_date_time_location(text):
	# Define regular expressions for matching date, time, and location
	date_regex = r'(\d{2}/\d{2})'
	time_regex = r'(\d{2}h\d{2})'
	location_regex = r'Salle \d+'

	# Initialize variables for date, time, and location
	date = None
	time = None
	location = None

	# Find date in the text
	date_match = re.search(date_regex, text)
	if date_match:
		date = date_match.group(1)

	# Find time in the text
	time_match = re.search(time_regex, text)
	if time_match:
		time = time_match.group(1)

	# Find location in the text
	location_match = re.search(location_regex, text)
	if location_match:
		location = location_match.group()

	return date, time, location



def preprocess_data(data):
	data["Description"] = data["Date"] + " - " + data["Time"] + " - " + data[
		"Location"] + " - " + data["Duration"].astype(str) + " min"
	current_year = datetime.now().year
	data['StartDatetime'] = pd.to_datetime(
		data['Date'] + '/' + str(current_year) + ' ' + data[
			'Time'].str.replace('h', ':'), dayfirst=True)
	data['EndDatetime'] = data['StartDatetime'] + pd.to_timedelta(
		data['Duration'], unit='m')
	data['Start'] = data['StartDatetime'].dt.strftime('%Y-%m-%dT%H:%M:%S')
	data['End'] = data['EndDatetime'].dt.strftime('%Y-%m-%dT%H:%M:%S')
	return data


# Example usage
if __name__ == "__main__":

	titles = []
	durations = []
	dates = []
	times = []
	locations = []
	img_urls = []

	for n in range(6, 18):
		target_url = f"https://www.etrangefestival.com/2022/fr/schedule/09-{str(n).zfill(2)}"
		target_div_class = "schedule_grid item-grid"

		urls_in_target_div = get_urls_from_div(target_url, target_div_class)
		session_urls = [url for url in urls_in_target_div if url != target_url]


		for url in session_urls:
			print(url)
			title, duration, seances, img_url = get_info_from_session_url(url)
			for date, info in seances.items():
				titles.append(title)
				durations.append(duration)
				dates.append(date)
				times.append(info['time'])
				locations.append(info['location'])
				img_urls.append(img_url)

	data_dict = {
				'Title': titles,
				'Duration': durations,
				'Date': dates,
				'Time': times,
				'Location': locations,
				'ImageURL': img_urls
			}

			# Create a pandas DataFrame from the dictionary
	df = pd.DataFrame(data_dict)
	df = df.drop_duplicates().reset_index(drop=True)
	df = preprocess_data(df)
	df.to_csv('data/etrange_festival_2022.csv', index=False)