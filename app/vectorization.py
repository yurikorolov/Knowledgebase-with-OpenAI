import json
import os
import sys
import psycopg2
from psycopg2.extras import Json
from transformers import AutoTokenizer, AutoModel
import numpy as np
import torch

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

TRANSFORMERS_CACHE_DIR = os.getenv('TRANSFORMERS_CACHE', './transformers_cache')

# Initialize tokenizer and model
model_name = "DeepPavlov/rubert-base-cased-conversational"
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=TRANSFORMERS_CACHE_DIR)
model = AutoModel.from_pretrained(model_name, cache_dir=TRANSFORMERS_CACHE_DIR)

# Function to get embeddings
def get_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()

# Connect to PostgreSQL and pgvector
def connect_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def store_vectors(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conn = connect_db()
    cur = conn.cursor()

    for entry in data:
        question = entry['q']
        answer = entry['a']

        q_embedding = get_embedding(question).tolist()
        a_embedding = get_embedding(answer).tolist()

        cur.execute(
            "INSERT INTO qa (q_embedding, q, a_embedding, a) VALUES (%s, %s, %s, %s)",
            (q_embedding, question, a_embedding, answer)
        )

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python vectorization.py <json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    store_vectors(json_file)
    print(f"Data vectorized and stored in DB from {json_file}")

