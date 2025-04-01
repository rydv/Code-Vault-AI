import re
import os
from pathlib import Path
import json
from typing import List, Dict, Tuple, Optional

def is_code_file(file_path: Path, extensions: List[str]) -> bool:
    """Check if the file is a code file based on its extension."""
    return file_path.suffix.lower() in extensions

def extract_comment_above_function(code: str, function_start_idx: int) -> str:
    """Extract any comments that appear directly above a function."""
    # Look for comments above the function (either // or /* style)
    lines = code[:function_start_idx].split('\n')
    
    # Reverse to start from the line directly above the function
    lines.reverse()
    
    comment_lines = []
    for line in lines:
        line = line.strip()
        if not line or line.isspace():
            continue
        
        # Check for comment lines
        if line.startswith('//'):
            comment_lines.insert(0, line[2:].strip())
        elif line.startswith('*') and not line.startswith('*/'):
            comment_lines.insert(0, line[1:].strip())
        elif line.startswith('/*'):
            comment_lines.insert(0, line[2:].strip())
            break
        else:
            # If we hit a non-comment line, stop
            break
    
    return ' '.join(comment_lines)

def extract_js_functions(code: str, file_path: str) -> List[Dict]:
    """
    Extract JavaScript functions and their metadata from code.
    Returns a list of dictionaries with function name, code, and metadata.
    """
    chunks = []
    
    # Regular expressions for different JavaScript patterns
    function_patterns = [
        # Regular function declarations
        r'(function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)\s*\{)',
        # Arrow functions with explicit name assignment
        r'(const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(\([^)]*\)|[a-zA-Z_$][a-zA-Z0-9_$]*)\s*=>\s*\{',
        # Class methods
        r'(([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)\s*\{)',
        # ES6 method shorthand in object literals or classes
        r'(([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*function\s*\([^)]*\)\s*\{)'
    ]
    
    # Combine patterns for a single pass
    combined_pattern = '|'.join(function_patterns)
    
    # Find all potential function declarations
    matches = list(re.finditer(combined_pattern, code))
    
    for i, match in enumerate(matches):
        # Find the start of the current function
        start_idx = match.start()
        
        # Extract function name
        if 'function' in match.group(0):
            # Regular function or method
            function_name = match.group(2) if len(match.groups()) > 1 else "anonymous_function"
        elif 'const' in match.group(0) or 'let' in match.group(0) or 'var' in match.group(0):
            # Arrow function with assignment
            function_name = match.group(2)
        else:
            # Class method or object method
            function_name = match.group(2) if len(match.groups()) > 1 else "anonymous_method"
        
        # Find the end of the function by matching braces
        brace_count = 0
        end_idx = start_idx
        
        # Start after the opening brace
        for idx, char in enumerate(code[start_idx:], start=start_idx):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    # Found closing brace
                    end_idx = idx + 1
                    break
        
        if end_idx <= start_idx:
            # If we couldn't properly identify function bounds, skip
            continue
        
        # Extract the complete function code
        function_code = code[start_idx:end_idx].strip()
        
        # Extract comment if available
        description = extract_comment_above_function(code, start_idx)
        
        chunks.append({
            'chunk_id': f"{os.path.basename(file_path)}_{i}",
            'file_path': file_path,
            'chunk_type': 'function',
            'name': function_name,
            'description': description,
            'code': function_code,
            'start_line': code[:start_idx].count('\n') + 1,
            'end_line': code[:end_idx].count('\n') + 1
        })
    
    return chunks

def extract_jsx_components(code: str, file_path: str) -> List[Dict]:
    """
    Extract React JSX components from code.
    """
    chunks = []
    
    # Pattern for functional components
    component_patterns = [
        # Functional component with function keyword
        r'function\s+([A-Z][a-zA-Z0-9_]*)\s*\([^)]*\)\s*\{',
        # Arrow function component with const/let/var
        r'(const|let|var)\s+([A-Z][a-zA-Z0-9_]*)\s*=\s*(\([^)]*\)|[a-zA-Z_$][a-zA-Z0-9_$]*)\s*=>\s*\{',
        # Class component
        r'class\s+([A-Z][a-zA-Z0-9_]*)\s+extends\s+React\.Component'
    ]
    
    # Combine patterns
    combined_pattern = '|'.join(component_patterns)
    
    # Find all components
    matches = list(re.finditer(combined_pattern, code))
    
    for i, match in enumerate(matches):
        start_idx = match.start()
        
        # Extract component name based on pattern type
        if 'function' in match.group(0):
            component_name = match.group(1)
        elif 'const' in match.group(0) or 'let' in match.group(0) or 'var' in match.group(0):
            component_name = match.group(2)
        elif 'class' in match.group(0):
            component_name = match.group(1)
        else:
            component_name = f"Component_{i}"
        
        # Find the end by matching braces (similar to function extraction)
        brace_count = 0
        end_idx = start_idx
        
        # Find opening brace first
        for idx, char in enumerate(code[start_idx:], start=start_idx):
            if char == '{':
                brace_count = 1
                start_search_idx = idx + 1
                break
        
        # Then find matching closing brace
        for idx, char in enumerate(code[start_search_idx:], start=start_search_idx):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    # Found matching closing brace
                    end_idx = idx + 1
                    break
        
        if end_idx <= start_idx:
            # If we couldn't properly identify component bounds, skip
            continue
        
        # Extract the complete component code
        component_code = code[start_idx:end_idx].strip()
        
        # Extract comment if available
        description = extract_comment_above_function(code, start_idx)
        
        chunks.append({
            'chunk_id': f"{os.path.basename(file_path)}_{i}",
            'file_path': file_path,
            'chunk_type': 'component',
            'name': component_name,
            'description': description,
            'code': component_code,
            'start_line': code[:start_idx].count('\n') + 1,
            'end_line': code[:end_idx].count('\n') + 1
        })
    
    return chunks

def process_file(file_path: Path, repo_name: str) -> List[Dict]:
    """Process a single code file, extract chunks and metadata."""
    chunks = []
    
    # Read the file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []
    
    # If the file is too small, treat it as a single chunk
    if len(code.split('\n')) < 15:  # Less than 15 lines
        chunks.append({
            'chunk_id': os.path.basename(file_path),
            'file_path': str(file_path),
            'chunk_type': 'file',
            'name': os.path.basename(file_path),
            'description': '',  # No easy way to extract file-level description
            'code': code,
            'start_line': 1,
            'end_line': code.count('\n') + 1,
            'repo_name': repo_name
        })
        return chunks
    
    # Extract functions and components
    if file_path.suffix.lower() == '.js':
        chunks.extend(extract_js_functions(code, str(file_path)))
    elif file_path.suffix.lower() == '.jsx':
        chunks.extend(extract_jsx_components(code, str(file_path)))
        # Also extract any JavaScript functions in the JSX file
        chunks.extend(extract_js_functions(code, str(file_path)))
    
    # Add repository name to all chunks
    for chunk in chunks:
        chunk['repo_name'] = repo_name
    
    # If no chunks were extracted, treat the entire file as one chunk
    if not chunks:
        chunks.append({
            'chunk_id': os.path.basename(file_path),
            'file_path': str(file_path),
            'chunk_type': 'file',
            'name': os.path.basename(file_path),
            'description': '',
            'code': code,
            'start_line': 1,
            'end_line': code.count('\n') + 1,
            'repo_name': repo_name
        })
    
    return chunks 