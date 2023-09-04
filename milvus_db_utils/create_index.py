import openai
import pandas as pd
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, \
	Collection, utility
import time
from milvus.utils import embed
import os
import dotenv

dotenv.load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_ENGINE = os.getenv("OPENAI_ENGINE")
MILVUS_HOST = os.getenv("MILVUS_HOST")
MILVUS_PORT = os.getenv("MILVUS_PORT")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
embedded_field = os.getenv("embedded_field")
DIMENSION = int(os.getenv("DIMENSION"))

if __name__ == "__main__":
	# Connect to Milvus
	connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)

	# Remove collection if it already exists
	if utility.has_collection(COLLECTION_NAME):
		utility.drop_collection(COLLECTION_NAME)

	# Create collection which includes the id, title, and embedding.
	fields = [
		FieldSchema(name='id', dtype=DataType.INT64, descrition='Ids',
		            is_primary=True, auto_id=False),
		FieldSchema(name=embedded_field, dtype=DataType.VARCHAR,
		            description='Title texts', max_length=200),
		FieldSchema(name=f'{embedded_field}_embedding',
		            dtype=DataType.FLOAT_VECTOR,
		            description='Embedding vectors', dim=DIMENSION)
	]
	schema = CollectionSchema(fields=fields)
	collection = Collection(name=COLLECTION_NAME, schema=schema)

	# Create an index for the collection.
	index_params = {
		'index_type': 'IVF_FLAT',
		'metric_type': 'L2',
		'params': {'nlist': 1024}
	}

	collection.create_index(field_name=f'{embedded_field}_embedding',
	                        index_params=index_params)

	# Insert each title and its embedding
	data = pd.read_csv("./data/etrange_festival_2023.csv")
	data.fillna("", inplace=True)
	for i in data.index:
		ins = [[i], [data[embedded_field][i][:50] if len(data[embedded_field][i]) > 50 else data[embedded_field][i]],
		       [embed(data[embedded_field][i])]]
		collection.insert(ins)
		print(
			f"Inserted {data[embedded_field][i]} : {embed(data[embedded_field][i])}")
		time.sleep(3)  # Free OpenAI account limited to 60 RPM

	connections.disconnect("default")
