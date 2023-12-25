import argparse
import logging
import os
import time

import dotenv
import openai
import pandas as pd
from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)

from config import DATA_PATH, index_params
from milvus_db_utils.utils import embed

# Load environment variables
dotenv.load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_ENGINE = os.getenv("OPENAI_ENGINE")
MILVUS_HOST = os.getenv("MILVUS_HOST")
MILVUS_PORT = os.getenv("MILVUS_PORT")
DIMENSION = int(os.getenv("DIMENSION"))

# Logging config
logging.basicConfig(level=logging.INFO)


def main(filename: str, embedded_field: str) -> None:
    data = get_data_from_csv(filename, embedded_field)

    # Connect to Milvus
    connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)

    # Get embeddings
    embedings = get_embeddings(data, embedded_field)

    # Create embedded index in Milvus
    index_names = [
        f'embedded_field_{index_param["index_type"]}_' f'{index_param["metric_type"]}'
        for index_param in index_params
    ]

    for i, index_name in enumerate(index_names):
        create_index(data, embedded_field, index_params[i], index_name, embedings)

    connections.disconnect("default")


def get_embeddings(data: pd.DataFrame, embedded_field: str) -> list:
    embeddings = []
    for i in data.index:
        try:
            embeddings.append(embed(data[embedded_field][i]))
            logging.info(
                f"Embedded {data[embedded_field][i]} : "
                f"{embed(data[embedded_field][i])}"
            )
        except openai.error.APIConnectionError:
            time.sleep(60)
            embeddings.append(embed(data[embedded_field][i]))
    return embeddings


def get_data_from_csv(filename: str, embedded_field: str) -> pd.DataFrame:
    data = pd.read_csv(os.path.join(DATA_PATH, filename))
    data.fillna("", inplace=True)

    try:
        assert embedded_field in data.columns
    except AssertionError:
        raise AssertionError(
            f"embedded_field {embedded_field} not found in data.columns: "
            f"{data.columns}"
        )

    return data


def get_args():
    parser = argparse.ArgumentParser(description="Create index on Milvus")
    parser.add_argument(
        "-f",
        "--filename",
        type=str,
        default="etrange_festival_2023.csv",
        help="Name of the csv file containing the data",
    )
    parser.add_argument(
        "-e",
        "--embeded_field",
        type=str,
        default="etrange_festival_2023.csv",
        help="Name of the csv file containing the data",
    )
    return parser.parse_args()


def create_index(
    data: pd.DataFrame,
    embedded_field: str,
    index_param: dict,
    index_name: str,
    embedings: list,
) -> None:
    data[index_name] = data[embedded_field]

    if utility.has_collection(index_name):
        utility.drop_collection(index_name)

    fields = [
        FieldSchema(
            name="id",
            dtype=DataType.INT64,
            descrition="Ids",
            is_primary=True,
            auto_id=False,
        ),
        FieldSchema(
            name=embedded_field,
            dtype=DataType.VARCHAR,
            description=embedded_field,
            max_length=200,
        ),
        FieldSchema(
            name=index_name,
            dtype=DataType.FLOAT_VECTOR,
            description="Embedding vectors",
            dim=DIMENSION,
        ),
    ]

    collection = create_an_empty_collection(
        fields=fields, index_name=index_name, index_param=index_param
    )

    insert_each_title_and_its_embedding(
        data=data,
        embedded_field=embedded_field,
        collection=collection,
        embedings=embedings,
    )


def create_an_empty_collection(
    fields: list, index_name: str, index_param: dict
) -> Collection:
    schema = CollectionSchema(fields=fields)
    collection = Collection(name=index_name, schema=schema)
    collection.create_index(field_name=index_name, index_params=index_param)
    return collection


def insert_each_title_and_its_embedding(
    data: pd.DataFrame, embedded_field: str, collection: Collection, embedings: list
) -> None:
    for i in data.index:
        ins = [
            [i],
            [
                data[embedded_field][i][:50]
                if len(data[embedded_field][i]) > 50
                else data[embedded_field][i]
            ],
            [embedings[i]],
        ]
        collection.insert(ins)

        logging.info(
            f"Inserted {data[embedded_field][i]} : " f"{embed(data[embedded_field][i])}"
        )


if __name__ == "__main__":
    args = get_args()
    main(args.filename, args.embeded_field)
