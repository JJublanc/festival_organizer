import openai
import pandas as pd
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, \
	Collection, utility
import time
from milvus_db_utils.utils import embed
import os
import dotenv
from config import embedded_field, collection_name, index_params

dotenv.load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_ENGINE = os.getenv("OPENAI_ENGINE")
MILVUS_HOST = os.getenv("MILVUS_HOST")
MILVUS_PORT = os.getenv("MILVUS_PORT")
DIMENSION = int(os.getenv("DIMENSION"))


def get_embeddings(data, embedded_field):
	embeddings = []
	for i in data.index:
		try:
			embeddings.append(embed(data[embedded_field][i]))
		# time.sleep(3)
		except openai.error.APIConnectionError:
			time.sleep(60)
			embeddings.append(embed(data[embedded_field][i]))
	return embeddings


if __name__ == "__main__":
	# Get data
	data = pd.read_csv("./data/etrange_festival_2023.csv")
	data.fillna("", inplace=True)

	# Connect to Milvus
	connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
	embedings = get_embeddings(data, embedded_field)

	index_names = [
		f'embedded_field_{index_param["index_type"]}_{index_param["metric_type"]}'
		for index_param in index_params]

	for i, index_name in enumerate(index_names):
		data[index_name] = data[embedded_field]
		if utility.has_collection(index_name):
			utility.drop_collection(index_name)
		fields = [
			FieldSchema(name='id', dtype=DataType.INT64, descrition='Ids',
			            is_primary=True, auto_id=False),
			FieldSchema(name=embedded_field, dtype=DataType.VARCHAR,
			            description=embedded_field, max_length=200),
			FieldSchema(name=index_name,
			            dtype=DataType.FLOAT_VECTOR,
			            description='Embedding vectors', dim=DIMENSION)
		]

		# Remove collection if it already exists
		schema = CollectionSchema(fields=fields)
		collection = Collection(name=index_name, schema=schema)
		collection.create_index(
			field_name=index_name,
			index_params=index_params[i])

		# Insert each title and its embedding
		for i in data.index:
			ins = [[i], [data[embedded_field][i][:50] if len(
				data[embedded_field][i]) > 50 else data[embedded_field][i]],
			       [embedings[i]]]
			collection.insert(ins)
		print(
			f"Inserted {data[embedded_field][i]} : "
			f"{embed(data[embedded_field][i])}")

	connections.disconnect("default")