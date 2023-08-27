import openai
import dotenv
import os
dotenv.load_dotenv()
OPENAI_ENGINE = os.getenv("OPENAI_ENGINE")
def embed(text):
	return openai.Embedding.create(
		input=text,
		engine=OPENAI_ENGINE)["data"][0]["embedding"]