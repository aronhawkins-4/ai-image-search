# AI Semantic Image Searcher

This project is an AI-powered semantic image search tool for local files. It allows you to search your local image collection using natural language queries, leveraging OpenAI's CLIP model for deep semantic understanding of both images and text.

## Features

- **Semantic Search:** Find images by describing their content in plain English (e.g., "woman riding a bike", "cooking dinner").
- **Local File Support:** Indexes and searches images from a local directory.
- **CLIP Model:** Uses OpenAI's CLIP (ViT-B/32) for robust image and text embeddings.
- **Vector Database:** Stores and searches image embeddings using ChromaDB for fast similarity search.
- **Automatic Embedding Management:** Automatically adds new images and updates the embedding database as your collection changes.
- **Visualization:** Displays the top matching images for your query.

## Requirements

- Python 3.8+
- [PyTorch](https://pytorch.org/)
- [CLIP](https://github.com/openai/CLIP)
- [ChromaDB](https://www.trychroma.com/)
- [Pillow](https://python-pillow.org/)
- [matplotlib](https://matplotlib.org/)
- [tqdm](https://tqdm.github.io/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

1. **Set the Image Directory**

   - By default, the script looks for images in `~/Downloads/`. You can change the `direc` variable in `main.py` to point to your desired image folder.

2. **Start ChromaDB Server**

   - Make sure you have a ChromaDB server running locally on port 8000 (or adjust the host/port in `main.py`).

3. **Run the Search**
   - Use the command line to search for images:

```bash
python3 main.py "your search text here"
```

Example:

```bash
python3 main.py "woman riding a bike"
```

The script will display the top 3 most relevant images matching your query.

## How It Works

- **Indexing:**

  - The script scans your image directory, computes CLIP embeddings for each image, and stores them in ChromaDB.
  - Embeddings are normalized for accurate cosine similarity search.
  - New images are automatically added to the database.

- **Searching:**
  - Your text query is embedded using CLIP and normalized.
  - The script queries ChromaDB for the most similar image embeddings.
  - The top results are displayed using matplotlib.

## Customization

- **Image Directory:**

  - Change the `direc` variable in `main.py` to point to any folder containing `.jpg` images.

- **Number of Results:**
  - Adjust the `n_results` parameter in the `collection.query` call to return more or fewer images.

## Troubleshooting

- **ChromaDB Connection:**

  - Ensure the ChromaDB server is running and accessible at the specified host/port.

- **Missing Dependencies:**

  - Install all required Python packages using the provided `requirements.txt`.

- **Image Format:**
  - Only `.jpg` images are indexed by default. Modify the `get_image_paths` function to support other formats if needed.

## License

This project is for educational and research purposes. See individual library licenses for details.
