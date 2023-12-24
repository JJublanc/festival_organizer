import os

import dotenv
import openai

dotenv.load_dotenv()
OPENAI_ENGINE = os.getenv("OPENAI_ENGINE")


def embed(text: str) -> list:
    return openai.Embedding.create(input=text, engine=OPENAI_ENGINE)["data"][0][
        "embedding"
    ]
