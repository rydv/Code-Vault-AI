import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import time
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

from config import (
    METADATA_CSV, EMBEDDINGS_CSV, EMBEDDINGS_DIR,
    EMBEDDING_MODEL, EMBEDDING_DIMENSIONS, MAX_CHUNK_SIZE
)

# Load environment variables from .env file
load_dotenv()

# Load the Sentence Transformer model
model = SentenceTransformer(EMBEDDING_MODEL)

def create_prompt_for_code_chunk(chunk_row):
    """
    Create a standardized prompt for the code chunk to get consistent embeddings.
    """
    chunk_type = chunk_row['chunk_type']
    name = chunk_row['name']
    repo = chunk_row['repo_name']
    file_path = chunk_row['file_path']
    description = chunk_row.get('description', '')
    code = chunk_row['code']
    
    prompt = f"Repository: {repo}\n"
    prompt += f"File: {file_path}\n"
    prompt += f"Type: {chunk_type}\n"
    prompt += f"Name: {name}\n"
    
    if description:
        prompt += f"Description: {description}\n"
    
    prompt += f"Code:\n{code}"
    
    return prompt

def generate_embedding(text):
    """
    Generate embedding for a text string using Sentence Transformers.
    """
    # Truncate if needed to fit within token limits
    if len(text) > MAX_CHUNK_SIZE:
        text = text[:MAX_CHUNK_SIZE]
    
    try:
        # Create embedding using Sentence Transformers
        embedding = model.encode(text)
        return embedding.tolist()  # Convert numpy array to list for easier storage
    
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # Return empty embedding on error
        return [0.0] * EMBEDDING_DIMENSIONS

def process_chunks_for_embeddings(metadata_df):
    """
    Process all code chunks and generate embeddings.
    """
    # Create an empty list to store embeddings and metadata
    embeddings_data = []
    
    # Process each chunk
    for idx, row in tqdm(metadata_df.iterrows(), total=len(metadata_df), desc="Generating embeddings"):
        # Create prompt text for this code chunk
        prompt_text = create_prompt_for_code_chunk(row)
        
        # Generate embedding
        embedding_vector = generate_embedding(prompt_text)
        
        # Add chunk metadata and embedding to results
        chunk_data = {
            'chunk_id': row['chunk_id'],
            'file_path': row['file_path'],
            'repo_name': row['repo_name'],
            'chunk_type': row['chunk_type'],
            'name': row['name'],
            'description': row.get('description', ''),
            'start_line': row['start_line'],
            'end_line': row['end_line'],
            'embedding': embedding_vector
        }
        
        embeddings_data.append(chunk_data)
        
        # No need for a delay with Sentence Transformers as there are no API rate limits
    
    return embeddings_data

def save_embeddings_to_csv(embeddings_data):
    """
    Save embeddings data to CSV file.
    The embeddings themselves are stored as JSON strings.
    """
    # Convert embeddings data to DataFrame
    df = pd.DataFrame(embeddings_data)
    
    # Convert embedding vectors to strings for CSV storage
    df['embedding'] = df['embedding'].apply(lambda x: str(x))
    
    # Save to CSV
    df.to_csv(EMBEDDINGS_CSV, index=False)
    
    return df

def main():
    """Main function to generate embeddings for code chunks."""
    # Make sure output directory exists
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
    
    # Check if metadata CSV exists
    if not os.path.exists(METADATA_CSV):
        print(f"Error: Metadata file {METADATA_CSV} does not exist. Run process_code.py first.")
        sys.exit(1)
    
    # Load metadata
    print(f"Loading metadata from {METADATA_CSV}")
    metadata_df = pd.read_csv(METADATA_CSV)
    
    # Generate embeddings
    print(f"Generating embeddings for {len(metadata_df)} code chunks using Sentence Transformers model: {EMBEDDING_MODEL}")
    embeddings_data = process_chunks_for_embeddings(metadata_df)
    
    # Save embeddings
    print(f"Saving embeddings to {EMBEDDINGS_CSV}")
    save_embeddings_to_csv(embeddings_data)
    
    print("Done!")

if __name__ == "__main__":
    main() 