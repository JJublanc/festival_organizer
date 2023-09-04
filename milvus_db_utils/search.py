from pymilvus import connections, FieldSchema, CollectionSchema, DataType, \
	Collection
from milvus.utils import embed
import os
import dotenv
import pandas as pd

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ENGINE = os.getenv("OPENAI_ENGINE")
MILVUS_HOST = os.getenv("MILVUS_HOST")
MILVUS_PORT = os.getenv("MILVUS_PORT")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
embedded_field = os.getenv("embedded_field")
DIMENSION = os.getenv("DIMENSION")

connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)

collection = Collection(name=COLLECTION_NAME)
collection.load()


# Search the database based on input text
def search(text):
	# Search parameters for the index
	search_params = {
		"metric_type": "L2"
	}

	results = collection.search(
		data=[embed(text)],  # Embeded search value
		anns_field=f"{embedded_field}_embedding",  # Search across embeddings
		param=search_params,
		limit=5,  # Limit to five results per search
		output_fields=[embedded_field, "id"]
	)

	ret = []
	for hit in results[0]:
		row = []
		row.extend([hit.id, hit.score, hit.entity.get(embedded_field)])
		ret.append(row)
	return ret


if __name__ == "__main__":
	data = pd.read_csv("./data/etrange_festival_2023.csv")
	for i in range(5):
		search_query = (input("Quel type de film cherchez-vous ? "))
		# search_query = "film d'horreur"
		for result in search(search_query):
			print(data.iloc[result[0],:])
			print(data.loc[result[0], "URL"])
			print("\n....\n")
