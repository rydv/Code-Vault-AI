import os
import sys
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import json

from config import (
    REPO_DIR, REPO_NAME, CODE_EXTENSIONS, 
    PROCESSED_DIR, METADATA_CSV
)
from code_parser import is_code_file, process_file

def find_code_files(repo_path: Path, extensions: list) -> list:
    """
    Find all code files in the repository with specified extensions.
    """
    code_files = []
    
    # Walk through all directories and files
    for root, dirs, files in os.walk(repo_path):
        # Skip node_modules and other unwanted directories
        if 'node_modules' in root or '.git' in root:
            continue
            
        # Add code files with matching extensions
        for file in files:
            file_path = Path(os.path.join(root, file))
            if is_code_file(file_path, extensions):
                code_files.append(file_path)
    
    return code_files

def process_repository(repo_path: Path, repo_name: str, extensions: list) -> pd.DataFrame:
    """
    Process all code files in a repository and extract chunks.
    Returns a DataFrame with code chunks and metadata.
    """
    # Find all code files
    code_files = find_code_files(repo_path, extensions)
    print(f"Found {len(code_files)} code files to process")
    
    all_chunks = []
    
    # Process each file
    for file_path in tqdm(code_files, desc="Processing files"):
        # Extract code chunks from the file
        chunks = process_file(file_path, repo_name)
        all_chunks.extend(chunks)
    
    # Convert to DataFrame
    if all_chunks:
        df = pd.DataFrame(all_chunks)
        return df
    else:
        print("No code chunks were extracted.")
        return pd.DataFrame()

def main():
    """Main function to process code repositories."""
    # Make sure output directory exists
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    print(f"Processing repository: {REPO_NAME}")
    print(f"Repository path: {REPO_DIR}")
    
    # Process the repository
    chunks_df = process_repository(REPO_DIR, REPO_NAME, CODE_EXTENSIONS)
    
    if not chunks_df.empty:
        # Save metadata to CSV
        chunks_df.to_csv(METADATA_CSV, index=False)
        print(f"Processed {len(chunks_df)} code chunks and saved metadata to {METADATA_CSV}")
    else:
        print("No data was processed.")

if __name__ == "__main__":
    main() 