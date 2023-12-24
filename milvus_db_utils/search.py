import os
import time

import dotenv
import pandas as pd
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections

from config import embedded_field, index_params
from milvus_db_utils.utils import embed

index_names = [
    f'embedded_field_{index_param["index_type"]}_{index_param["metric_type"]}'
    for index_param in index_params
]

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ENGINE = os.getenv("OPENAI_ENGINE")
MILVUS_HOST = os.getenv("MILVUS_HOST")
MILVUS_PORT = os.getenv("MILVUS_PORT")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
DIMENSION = os.getenv("DIMENSION")

connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)


# Search the database based on input text
def search(text, index_param, collection):
    # Search parameters for the index
    index_name = (
        f'embedded_field_{index_param["index_type"]}_{index_param["metric_type"]}'
    )
    search_params = {
        "metric_type": index_param["metric_type"],
    }

    results = collection.search(
        data=[embed(text)],  # Embeded search value
        anns_field=index_name,  # Search across embeddings
        param=search_params,
        limit=5,  # Limit to five results per search
        output_fields=[embedded_field, "id"],
    )

    ret = []
    for hit in results[0]:
        row = []
        row.extend([hit.id, hit.score, hit.entity.get(embedded_field)])
        ret.append(row)
    return ret


if __name__ == "__main__":
    data = pd.read_csv("./data/etrange_festival_2023.csv")

    results = pd.DataFrame(
        columns=[
            "id",
            "score",
            "embedded_field",
            "URL",
            "Title",
            "Description",
            "search_query",
            "index_type",
            "metric_type",
        ]
    )
    search_queries = ["film d'horreur", "film érotique", "film de science-fiction"]
    for search_query in search_queries:
        for i, index_param in enumerate(index_params):
            collection_name = f'embedded_field_{index_param["index_type"]}_{index_param["metric_type"]}'
            collection = Collection(name=collection_name)
            collection.load()
            t = time.time()
            searches = search(search_query, index_param, collection)
            t = time.time() - t
            for result in searches:
                print(data.iloc[result[0], :])
                print(data.loc[result[0], "URL"])
                print("\n....\n")

                results = pd.concat(
                    [
                        results,
                        pd.DataFrame(
                            [
                                {
                                    "id": result[0],
                                    "score": result[1],
                                    "embedded_field": result[2],
                                    "URL": data.loc[result[0], "URL"],
                                    "Title": data.loc[result[0], "Title"],
                                    "Description": data.loc[result[0], "Description"],
                                    "search_query": search_query,
                                    "index_type": index_params[i]["index_type"],
                                    "metric_type": index_params[i]["metric_type"],
                                    "delta_time_query": t,
                                }
                            ]
                        ),
                    ],
                    ignore_index=True,
                )

    results.to_csv("./data/search_results.csv", index=False)
