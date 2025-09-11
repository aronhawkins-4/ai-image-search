#!/usr/bin/env python3

# Import in a specific order to avoid segfault issues
# Core Python and basic scientific computing first
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib
from PIL import Image
import numpy as np
import clip
import torch
import os
import json
import pickle
from typing import List, Union, Tuple
import chromadb
import argparse

chromadb_client = chromadb.HttpClient(host="localhost", port=8000)
print(f"Chromadb collection size: {len(chromadb_client.list_collections())}")
# Load environment early
load_dotenv()
# os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Torch and clip next (this is the critical section)
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load CLIP model early, before other heavy imports
print("Loading CLIP model...")
model, preprocess = clip.load("ViT-B/32", device=device)
print("CLIP model loaded successfully!")

# Now safe to import other modules

# Set matplotlib backend before importing pyplot

# Optional heavy imports - only if needed
# try:
# import faiss
# print("FAISS loaded successfully")
# except ImportError:
# print("FAISS not available")
# faiss = None

try:
    from datasets import Dataset
    from torch.utils.data import DataLoader
    import torch.nn as nn
    from tqdm import tqdm
    print("ML utilities loaded successfully")
except ImportError as e:
    print(f"Some ML utilities not available: {e}")
    sys.exit(1)

try:
    from openai import OpenAI
    import base64
    import sys
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI()
        print("OpenAI client initialized")
    else:
        print("Warning: OPENAI_API_KEY not found in environment")
        client = None
except ImportError:
    print("OpenAI not available")
    client = None


def get_image_paths(directory: str) -> List[str]:
    image_paths = []
    for filename in os.listdir(directory):
        if filename.endswith('.jpg'):
            image_paths.append(os.path.join(directory, filename))
    return image_paths


direc = os.path.expanduser('~/Downloads/')
# direc = os.path.expanduser('~/Documents/Projects/ai-image-search/images/')
image_paths = get_image_paths(direc)


def get_features_from_image_path(image_paths):
    images = [preprocess(Image.open(image_path).convert("RGB"))
              for image_path in image_paths]
    # Ensure all items are tensors before stacking
    images = [img if isinstance(img, torch.Tensor) else torch.from_numpy(
        np.array(img)) for img in images]
    image_input = torch.stack(images)
    with torch.no_grad():
        image_features = model.encode_image(image_input).float().cpu().numpy()
    # Normalize embeddings (L2 norm)
    norms = np.linalg.norm(image_features, ord=2, axis=1, keepdims=True)
    image_features = image_features / norms
    return image_features


# image_features = get_features_from_image_path(image_paths)

collection = chromadb_client.get_or_create_collection('image_collection')
# Get existing IDs and paths from the collection
existing = collection.get(include=['metadatas', 'embeddings'])
existing_paths = set()
existing_id_by_path = {}
if existing and 'metadatas' in existing and existing['metadatas']:
    for idx, meta in enumerate(existing['metadatas']):
        if meta and 'path' in meta:
            existing_paths.add(meta['path'])
            existing_id_by_path[meta['path']] = existing['ids'][idx]
id_offset = len(existing['ids']) if existing and 'ids' in existing else 0
image_embedding_shape = len(
    existing['embeddings'][0]) if existing and 'embeddings' in existing and existing['embeddings'] is not None and len(existing['embeddings']) > 0 else None
for i, img_path in enumerate(image_paths):
    img_id = str(i + id_offset)
    meta = {'path': img_path}
    if img_path in existing_paths:
        # Replace existing embedding and metadata
        # collection.update(ids=[existing_id_by_path[img_path]], embeddings=[
        #                   embedding.tolist()], metadatas=[meta])
        print(f"Image already in collection: {img_path}, skipping add.")
    else:
        # Add new image
        try:
            embedding = get_features_from_image_path([img_path])[0]
            collection.add(embeddings=[embedding.tolist()], ids=[
                           img_id], metadatas=[meta])
            print(f"Added image to collection: {img_path}")
            if image_embedding_shape is None:
                image_embedding_shape = len(embedding)
        except Exception as e:
            print(f"Error adding image {img_path} to collection: {e}")

# Simple PyTorch Dataset for text


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


parser = argparse.ArgumentParser(
    description="Search for images using a text prompt.")
parser.add_argument("search_text", type=str, help="Text prompt to search for")
args = parser.parse_args()
search_text = args.search_text
print(f"Searching for text: {search_text}")
with torch.no_grad():
    text_search_embedding = encode_text([search_text], batch_size=32)
# Ensure shape matches image_features (should be [1, feature_dim])
if text_search_embedding.shape[-1] != image_embedding_shape:
    raise ValueError(
        f"Shape mismatch: text_search_embedding shape {text_search_embedding.shape}, image_features shape {image_embedding_shape}")
if len(text_search_embedding.shape) == 1:
    text_search_embedding = text_search_embedding.reshape(1, -1)
elif text_search_embedding.shape[0] != 1:
    text_search_embedding = text_search_embedding[:1]
query_results = collection.query(
    query_embeddings=text_search_embedding.astype(np.float32), n_results=3)
if (query_results is None) or (len(query_results['ids']) == 0):
    print("No results found.")
    exit(0)
metadatas = query_results.get('metadatas')
distances = query_results.get('distances')
if metadatas and len(metadatas) > 0 and metadatas[0]:
    for idx, metadata in enumerate(metadatas[0]):
        path = metadata.get('path') if metadata else None
        distance = distances[0][idx] if distances and len(
            distances) > 0 and distances[0] else None
        if isinstance(path, str) and os.path.isfile(path):
            im = Image.open(path)
            plt.imshow(im)
            plt.show()
        else:
            print(f"Invalid or missing image path: {path}")
else:
    print("No valid metadata found in query results.")
