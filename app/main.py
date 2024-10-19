import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import numpy as np
from scipy.spatial.distance import cosine
from transformers import AutoTokenizer, AutoModel
import torch
import queue

app = FastAPI()

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# GPT-4 rate limiting (in requests per minute)
MAX_REQUESTS_PER_MINUTE = 3
REQUEST_QUEUE = queue.Queue()

# Connect to PostgreSQL
def connect_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

class Question(BaseModel):
    q: str

# Tokenizer and model
model_name = "DeepPavlov/rubert-base-cased-conversational"
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=os.getenv('TRANSFORMERS_CACHE'))
model = AutoModel.from_pretrained(model_name, cache_dir=os.getenv('TRANSFORMERS_CACHE'))

# Function to get embeddings
def get_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()

# Function to search the database
def search_db(query_embedding):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT id, q_embedding, a FROM qa")
    rows = cur.fetchall()

    results = []
    for row in rows:
        q_embedding = np.array(row[1])
        similarity = 1 - cosine(query_embedding, q_embedding)
        results.append((similarity, row[2]))

    results.sort(key=lambda x: x[0], reverse=True)
    cur.close()
    conn.close()

    return results[:3]

@app.post("/search")
async def search(question: Question):
    # Get question embedding
    q_embedding = get_embedding(question.q)

    # Perform search in DB
    results = search_db(q_embedding)

    # Add top 3 answers to GPT-4 context
    context = "\n\n".join([result[1] for result in results])

    # Add request to the queue
    if REQUEST_QUEUE.qsize() < MAX_REQUESTS_PER_MINUTE:
        REQUEST_QUEUE.put(context)
        return {"message": "Request added to queue", "queue_id": REQUEST_QUEUE.qsize()}
    else:
        raise HTTPException(status_code=429, detail="Too many requests, try later.")

@app.get("/queue/{queue_id}")
async def check_queue(queue_id: int):
    if queue_id <= REQUEST_QUEUE.qsize():
        context = REQUEST_QUEUE.get()
        # Perform OpenAI API request here
        return {"status": "processed", "context": context}
    else:
        return {"status": "waiting"}

