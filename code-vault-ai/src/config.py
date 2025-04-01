import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directories
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = ROOT_DIR / "data"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
PROCESSED_DIR = DATA_DIR / "processed"

# Repository configuration
REPO_DIR = Path("../libraries/javascript/e-commerce")
REPO_NAME = "e-commerce"

# File extensions to process
CODE_EXTENSIONS = [".js", ".jsx", ".json"]

# Sentence Transformers configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # A lightweight model suitable for code embeddings
EMBEDDING_DIMENSIONS = 384  # Dimensions for all-MiniLM-L6-v2 model

# Chunk size limitations (in characters)
MAX_CHUNK_SIZE = 8000  # Maximum size for a chunk to generate embeddings

# Output configuration
METADATA_CSV = PROCESSED_DIR / "metadata.csv"
EMBEDDINGS_CSV = EMBEDDINGS_DIR / "embeddings.csv" 