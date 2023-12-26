# My Movie Festival Application
This application was built using Python and Streamlit, and it is designed to
help users easily select and organize movie events for their own personalized
movie festival.


https://github.com/JJublanc/festival_organizer/assets/45565888/7acb8d61-4491-4b55-96c6-9c63570d5d74


## Features
* Movie search and selection from a curated list
* Display of selected movies in a convenient calendar view
* Identification of overlapping movie timings
* Saving of selected movie list to a file
* Generation of iCalendar (.ics) file for selected events
* Theme customization options (wide mode and light mode)

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
poetry add <package_name> --group dev # For development dependencies like
                                      # testing libraries
```

## Set you environment variables
```
ROOT_PATH = <path to the root of the project>
DIMENSION = 1536  # Embeddings size
COUNT = 100  # How many titles to embed and insert.
MILVUS_HOST = 'localhost'  # Milvus server URI
MILVUS_PORT = '19530' # Milvus server port
OPENAI_ENGINE = <which_engine_to_use>
OPENAI_API_KEY = <use your own Open AI API Key here>
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

## Pre-commit
```
poetry add pre-commit --group dev
pre-commit install
```


## Contributing
Contributions to this application are welcome. Please fork this repository and create a pull request if you have something you want to add or change.


## Licenses
This application use packages such as protobuf which is licence under the BSD 3-Clause License. Please refer to the LICENSE file for more information. https://opensource.org/license/bsd-3-clause/
Other packages are under the Apache 2.0 License. Please refer to the LICENSE file for more information. https://opensource.org/licenses/Apache-2.0
For more informatio about licence, please refer to the file licenses.md
