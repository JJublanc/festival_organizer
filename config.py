import os

import dotenv

dotenv.load_dotenv()

# PATHS
ROOT_PATH = os.getenv("ROOT_PATH")
DATA_PATH = os.path.join(ROOT_PATH, "data")

# MILVUS VARS
index_params = [
    {"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 1024}},
    {
        "index_type": "HNSW",
        "metric_type": "L2",
        "params": {"M": 4, "efConstruction": 16},
    },
]

collection_name = "festival_movies_db"  # Collection name
embedded_field = "Description_movie_full"  # Field name of the embedding vectors
