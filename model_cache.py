import os
from transformers import AutoModel, AutoTokenizer

# Get the model name and cache directory from environment variables
MODEL_NAME = os.getenv("MODEL_NAME", "DeepPavlov/rubert-base-cased-conversational")
TRANSFORMERS_CACHE = os.getenv("TRANSFORMERS_CACHE", "/root/.cache/huggingface/transformers")

# Paths to check for the cached model files
model_cache_path = os.path.join(TRANSFORMERS_CACHE, MODEL_NAME.replace("/", "_"))

def is_model_cached(cache_path):
    """Check if the model is already cached."""
    if os.path.exists(cache_path):
        print(f"Model {MODEL_NAME} is already cached at {cache_path}")
        return True
    return False

def download_model():
    """Download the model and tokenizer."""
    print(f"Downloading the model {MODEL_NAME}...")
    AutoModel.from_pretrained(MODEL_NAME, cache_dir=TRANSFORMERS_CACHE)
    AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=TRANSFORMERS_CACHE)
    print(f"Model {MODEL_NAME} downloaded successfully.")

if __name__ == "__main__":
    if not is_model_cached(model_cache_path):
        download_model()
    else:
        print(f"Skipping download. Model is already cached.")
 
