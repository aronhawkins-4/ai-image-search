from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import torch
from PIL import Image
import io
import chromadb
from transformers import CLIPProcessor, CLIPModel
import clip
from typing import List
from torch.utils.data import DataLoader
from tqdm import tqdm
import numpy as np
import json

# Torch and clip next (this is the critical section)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load CLIP model early, before other heavy imports
model, preprocess = clip.load("ViT-B/32", device=device)

# ChromaDB setup
chromadb_client = chromadb.HttpClient(host="localhost", port=8000)
collection = chromadb_client.get_or_create_collection("image_collection")

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# OAuth2 setup (dummy for example)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")

# Dummy user authentication


def fake_decode_token(token):
    if token == "secret-token":
        return {"username": "user"}
    raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    return fake_decode_token(token)


# Auth endpoint


class AuthRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@app.post("/auth", response_model=AuthResponse)
async def auth(auth_req: AuthRequest):
    # Dummy authentication logic
    if auth_req.username == "user" and auth_req.password == "password":
        return AuthResponse(access_token="secret-token")
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Generate endpoint


# @app.post("/generate")
# async def generate(
#     file: UploadFile = File(...),
#     user: dict = Depends(get_current_user)
# ):
#     # image_bytes = await file.read()
#     # image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#     # inputs = clip_processor(images=image, return_tensors="pt")
#     # with torch.no_grad():
#     #     image_embeds = clip_model.get_image_features(
#     #         pixel_values=inputs["pixel_values"])  # type: ignore
#     # image_embeds = image_embeds.cpu().numpy()[0].tolist()
#     # # Store in ChromaDB
#     # filename = file.filename or "unknown"
#     # collection.add(
#     #     embeddings=[image_embeds],
#     #     documents=[filename],
#     #     ids=[filename]
#     # )
#     return {"message": "Image embedding stored", "id": "filename"}
# Query endpoint


class QueryRequest(BaseModel):
    query: str
    top_k: int = 24
    offset: int = 0


@app.post("/query")
async def query(
    req: QueryRequest,
    user: dict = Depends(get_current_user)
):
    print(
        f"Received query: {req.query}, top_k: {req.top_k}, offset: {req.offset}")
    with torch.no_grad():
        text_search_embedding = encode_text([req.query], batch_size=32)
    results = collection.query(
        query_embeddings=text_search_embedding.astype(np.float32),
        n_results=req.top_k + req.offset
    )
    # Apply offset manually to the results
    if "documents" in results:
        for key in results:
            print(key)
            if (isinstance(results[key], list) and len(results[key]) > 0 and isinstance(results[key][0], list)):
                results[key] = [results[key][0]
                                [req.offset:req.offset + req.top_k]]
            # results[key] = results[key][0][req.offset:req.offset + req.top_k]
    # print(f"Query results: {json.dumps(results, indent=2)}")
    return {"results": results}


class GetImagesRequest(BaseModel):
    offset: int = 0


@app.get("/get-images")
async def get_images(
    req: GetImagesRequest = Depends(),
    user: dict = Depends(get_current_user)
):
    results = collection.get(limit=24, offset=req.offset)
    return {"results": results}
