import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import json
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import ast  # For safely evaluating the string representation of embeddings

from config import (
    EMBEDDINGS_CSV, EMBEDDING_MODEL, EMBEDDING_DIMENSIONS
)

# Load environment variables from .env file
load_dotenv()

# Load the Sentence Transformer model
model = SentenceTransformer(EMBEDDING_MODEL)

def load_embeddings():
    """
    Load embeddings from CSV file.
    """
    if not os.path.exists(EMBEDDINGS_CSV):
        print(f"Error: Embeddings file {EMBEDDINGS_CSV} does not exist.")
        sys.exit(1)
    
    # Load the embeddings DataFrame
    df = pd.read_csv(EMBEDDINGS_CSV)
    
    # Convert embedding strings back to vectors
    df['embedding'] = df['embedding'].apply(lambda x: ast.literal_eval(x))
    
    return df

def generate_query_embedding(query_text):
    """
    Generate embedding for a query using Sentence Transformers.
    """
    try:
        # Create embedding using Sentence Transformers
        embedding = model.encode(query_text)
        return embedding.tolist()  # Convert numpy array to list
    
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        return None

def calculate_similarity(query_embedding, code_embedding):
    """
    Calculate cosine similarity between query and code embeddings.
    """
    # Convert to numpy arrays
    query_vec = np.array(query_embedding)
    code_vec = np.array(code_embedding)
    
    # Calculate cosine similarity
    similarity = np.dot(query_vec, code_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(code_vec))
    
    return similarity

def search_code(query, embeddings_df, top_n=5):
    """
    Search for code chunks that match the query.
    """
    # Generate embedding for the query
    query_embedding = generate_query_embedding(query)
    
    if query_embedding is None:
        print("Error generating query embedding.")
        return []
    
    # Calculate similarity scores for all chunks
    embeddings_df['similarity'] = embeddings_df['embedding'].apply(
        lambda x: calculate_similarity(query_embedding, x)
    )
    
    # Sort by similarity (highest first)
    results = embeddings_df.sort_values('similarity', ascending=False).head(top_n)
    
    # Drop the embedding column for cleaner output
    results = results.drop(columns=['embedding'])
    
    return results

def display_results(results):
    """
    Display search results in a readable format.
    """
    if results.empty:
        print("No results found.")
        return
    
    print(f"\nFound {len(results)} results:\n")
    
    for idx, row in results.iterrows():
        print(f"#{idx+1} - {row['name']} ({row['chunk_type']}) - Similarity: {row['similarity']:.4f}")
        print(f"  Repository: {row['repo_name']}")
        print(f"  File: {row['file_path']}")
        print(f"  Lines: {int(row['start_line'])}-{int(row['end_line'])}")
        
        if row['description']:
            print(f"  Description: {row['description']}")
        
        print("-" * 80)

def main():
    """Main function to search for code based on a query."""
    # Get query from command line arguments
    if len(sys.argv) < 2:
        print("Usage: python query_code.py \"your query here\"")
        sys.exit(1)
    
    query = sys.argv[1]
    
    # Load embeddings
    print("Loading code embeddings...")
    embeddings_df = load_embeddings()
    
    # Search for code
    print(f"Searching for: {query}")
    results = search_code(query, embeddings_df)
    
    # Display results
    display_results(results)

if __name__ == "__main__":
    main() 