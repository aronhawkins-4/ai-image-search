#!/usr/bin/env python3

# Import in a specific order to avoid segfault issues
# Core Python and basic scientific computing first
from dotenv import load_dotenv
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
# print(f"Chromadb collection size: {len(chromadb_client.list_collections())}")
# Load environment early
load_dotenv()
# os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

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
    # print("ML utilities loaded successfully")
except ImportError as e:
    # print(f"Some ML utilities not available: {e}")
    sys.exit(1)

try:
    from openai import OpenAI
    import base64
    import sys
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI()
        # print("OpenAI client initialized")
    else:
        # print("Warning: OPENAI_API_KEY not found in environment")
        client = None
except ImportError:
    # print("OpenAI not available")
    client = None


def get_image_paths(directory: str) -> List[str]:
    image_paths = []
    for filename in os.listdir(directory):
        if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg'):
            image_paths.append(os.path.join(directory, filename))
    return image_paths


direc = os.path.expanduser(
    '~/Downloads/')
image_paths = get_image_paths(direc)

print(f"Found {len(image_paths)} images in directory {direc}")


def get_features_from_image_path(image_paths):
    from PIL import UnidentifiedImageError
    images = []
    for image_path in image_paths:
        if not os.path.exists(image_path) or not os.path.isfile(image_path):
            print(
                f"Image file does not exist or has not been downloaded: {image_path}")
            continue
        try:
            with Image.open(image_path) as img:
                if img.size[0] > 0 and img.size[1] > 0:
                    img = img.convert("RGB")
                    images.append(preprocess(img))
                else:
                    print(f"Skipping image with invalid size: {image_path}")
        except UnidentifiedImageError:
            print(f"Cannot identify image file: {image_path}")
            continue
        except Exception as e:
            print(f"Error opening image {image_path}: {e}")
            continue
    if not images:
        return []
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


image_features = get_features_from_image_path(image_paths)

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
        embedding = get_features_from_image_path([img_path])[0]
        collection.update(ids=[existing_id_by_path[img_path]], embeddings=[
                          embedding.tolist()], metadatas=[meta])
        print(f"Image already in collection: {img_path}, skipping add.")
        continue
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
            continue
