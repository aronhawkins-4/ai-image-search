#!/usr/bin/env python3

# Import in a specific order to avoid segfault issues
# Core Python and basic scientific computing first
from dotenv import load_dotenv
import numpy as np
import clip
import torch
import os
import json
from typing import List, Union, Tuple
import chromadb
import argparse

chromadb_client = chromadb.HttpClient(host="localhost", port=8000)
load_dotenv()


# Torch and clip next (this is the critical section)
device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"Using device: {device}")

# Load CLIP model early, before other heavy imports
# print("Loading CLIP model...")
model, preprocess = clip.load("ViT-B/32", device=device)

try:
    from datasets import Dataset
    from torch.utils.data import DataLoader
    import torch.nn as nn
    from tqdm import tqdm
except ImportError as e:
    sys.exit(1)

try:
    from openai import OpenAI
    import base64
    import sys
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI()
    else:
        client = None
except ImportError:
    client = None


collection = chromadb_client.get_or_create_collection('image_collection')


class SimpleTextDataset(torch.utils.data.Dataset):
    def __init__(self, texts):
        self.texts = texts

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        return clip.tokenize(self.texts[idx], context_length=77)[0]


def encode_text(text: List[str], batch_size: int):
    dataset = SimpleTextDataset(text)
    dataloader = DataLoader(dataset, batch_size=batch_size)
    text_embeddings = []
    pbar = tqdm(total=(len(text) + batch_size - 1) // batch_size, position=0)
    with torch.no_grad():
        for batch in dataloader:
            batch = batch.to(device)
            text_emb = model.encode_text(batch).detach().cpu().numpy()
            # Normalize each embedding in the batch
            text_emb = text_emb / \
                np.linalg.norm(text_emb, ord=2, axis=1, keepdims=True)
            text_embeddings.extend(text_emb)
            pbar.update(1)
    pbar.close()
    return np.stack(text_embeddings)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search for images using a text prompt.")
    parser.add_argument("search_text", type=str,
                        help="Text prompt to search for")
    args = parser.parse_args()
    search_text = args.search_text

    with torch.no_grad():
        text_search_embedding = encode_text([search_text], batch_size=32)
    # Ensure shape matches image_features (should be [1, feature_dim])
    # if text_search_embedding.shape[-1] != image_embedding_shape:
        # raise ValueError(
        # f"Shape mismatch: text_search_embedding shape {text_search_embedding.shape}, image_features shape {image_embedding_shape}")
    # if len(text_search_embedding.shape) == 1:
        # text_search_embedding = text_search_embedding.reshape(1, -1)
    # elif text_search_embedding.shape[0] != 1:
        # text_search_embedding = text_search_embedding[:1]
    query_results = collection.query(
        query_embeddings=text_search_embedding.astype(np.float32), n_results=24)
    print(json.dumps(query_results, indent=2))
