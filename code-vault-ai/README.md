# Code Vault AI - POC

A proof-of-concept implementation for creating and querying embeddings of code from organizational repositories.

## Directory Structure

```
code-vault-ai/
├── data/
│   ├── embeddings/  # Storage for generated embeddings
│   └── processed/   # Storage for processed code metadata
├── src/
│   ├── config.py           # Configuration settings
│   ├── code_parser.py      # Code parsing utilities
│   ├── process_code.py     # Process code files into chunks
│   ├── generate_embeddings.py  # Generate embeddings for chunks
│   └── query_code.py       # Query the code using natural language
├── .env.example       # Example environment variables file
└── requirements.txt   # Python dependencies
```

## Setup Instructions

1. Clone this repository:
   ```
   git clone <repo-url>
   cd code-vault-ai
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Update the repository path in `src/config.py` if needed:
   ```python
   REPO_DIR = Path("../libraries/javascript/e-commerce")  # Update this path
   REPO_NAME = "e-commerce"  # Update this name
   ```

## Usage

### Step 1: Process Code Files

Process the code files to extract functions, components, and other logical chunks:

```
python src/process_code.py
```

This will create a `metadata.csv` file in the `data/processed/` directory.

### Step 2: Generate Embeddings

Generate embeddings for each code chunk using Sentence Transformers:

```
python src/generate_embeddings.py
```

This will create an `embeddings.csv` file in the `data/embeddings/` directory.

### Step 3: Query Code

Search for code using natural language queries:

```
python src/query_code.py "how to handle user authentication"
```

This will return the most relevant code snippets from your repository based on semantic similarity.

## Notes

- This is a minimal POC implementation and may need refinement for production use.
- The current implementation uses simple regex-based code parsing, which might not capture all code structures perfectly.
- The code chunking logic may need adjustments based on your specific codebase and languages.
- The project uses Sentence Transformers, which is free and runs locally without API costs.

## Future Improvements

- Add support for more programming languages
- Improve code structure parsing with AST-based approaches
- Implement a simple web UI for querying
- Add filtering options by repository, language, etc.
- Integrate with a vector database for more efficient searching
- Experiment with different Sentence Transformer models for better code understanding 