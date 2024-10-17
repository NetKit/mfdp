from sentence_transformers import SentenceTransformer

EMBEDDINGS_MODEL = "intfloat/multilingual-e5-large-instruct"

model = SentenceTransformer(EMBEDDINGS_MODEL)
