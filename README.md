# My Movie Festival Application
This application was built using Python and Streamlit, and it is designed to 
help users easily select and organize movie events for their own personalized 
movie festival.

## Features
Movie search and selection from a curated list
Display of selected movies in a convenient calendar view
Identification of overlapping movie timings
Saving of selected movie list to a file
Generation of iCalendar (.ics) file for selected events
Theme customization options (wide mode and light mode)
Seamless integration with Google Calendar (authentication through Google OAuth2)
Installation and Running
Clone this repository: git clone git@github.com:JJublanc/festival_organizer.git
Navigate to the cloned directory.
Install the required Python packages: pip install -r requirements.txt
Run the Streamlit application: streamlit run app.py

# Set up
## Requirements
* Python 3.9.4 or higher, but not 3.9.7
* Poetry 1.4.2 or higher
* An openai API key

## Create a virtual environment and install dependencies
```
pyenv local 3.9.4 
poetry config virtualenvs.in-project true
poetry install
poetry shell # Activate the virtual environment
```

## Add a dependency
```
poetry add <package_name>
poetry add <package_name> --dev # For development dependencies like 
                                # testing libraries
```

## Set you environment variables
```
COLLECTION_NAME = <Collection name>
DIMENSION = 1536  # Embeddings size
COUNT = 100  # How many titles to embed and insert.
MILVUS_HOST = 'localhost'  # Milvus server URI
MILVUS_PORT = '19530' # Milvus server port
OPENAI_ENGINE = <which_engine_to_use>
OPENAI_API_KEY = <use your own Open AI API Key here>
embedded_field = "Description_movie"
```

## Milvus database

For a simple use, you can install Milvus Standalone following the instructions 
below:
* https://milvus.io/docs/install_standalone-docker.md

Then you can run Milvus with the following command:
```
cd milvus_db_utils/
docker compose up -d
```

## Contributing
Contributions to this application are welcome. Please fork this repository and create a pull request if you have something you want to add or change.
