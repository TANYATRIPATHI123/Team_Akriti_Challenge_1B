# Approach Explanation for main.py

This document provides a detailed breakdown of the logic and approach used in main.py, the entry point for our PDF semantic extraction solution.

## Objective

The main goal of main.py is to:

- Read a structured input.json file describing a *user persona, **task, and associated **PDF documents*.
- Process each document to extract meaningful textual content.
- Compute *semantic similarity* between the extracted content and the user’s objective.
- Output the *top 5 most relevant sections* in a structured JSON format.

## High-Level Structure

### 1. *Imports and Model Initialization*

python
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')


- Loads a pre-trained sentence transformer model only *once* for efficiency.
- This model generates semantic embeddings for both the *goal text* and *PDF content*.

### 2. **extract_pdf_data(pdf_path)**

This function handles *PDF parsing* using PyMuPDF.

- Opens the PDF.
- Iterates over each page and extracts text blocks.
- Filters out short or non-textual blocks (less than 10 characters).
- Returns a list of dictionaries with:
    - title
    - page number
    - text content

*Purpose*: Cleanly extract relevant chunks of readable content from each page.

### 3. **process_collection(collection_path, output_dir)**

This function processes *one folder* (or collection) at a time.

### Steps:

1. **Read input.json**:
    - Extracts:
        - persona (e.g., "student")
        - job_to_be_done (e.g., "prepare for an exam")
        - documents (list of PDFs to process)
    - Forms a *semantic goal statement*:
        - As a {persona}, I need to {job_to_be_done}.
2. *Extract PDF Text*:
    - For each filename in the documents list:
        - Loads the file from PDFs/
        - Calls extract_pdf_data() to extract clean blocks of text
        - Aggregates all extracted content from all PDFs
3. *Compute Semantic Similarity*:
    - Encodes the goal statement into an embedding.
    - Encodes all text chunks into embeddings.
    - Uses cosine similarity to compare goal embedding vs. content embeddings.
    - Ranks all chunks and picks the *top 5* most relevant.
4. *Build Output JSON*:
    - Top 5 chunks are stored in:
        - extracted_sections: Metadata view
        - subsection_analysis: Full content view
    - Output includes processing timestamp, input metadata, and relevance ranking.
    - Writes a file named collectionname_output.json into the outputs/ folder.

### 4. **main() Function**

This is the entry point.

- Scans the /inputs directory.
- Detects all folders (collections) inside.
- For each folder:
    - Calls process_collection().

*Directory Assumptions*:


inputs/
└── collection_name/
    ├── input.json
    └── PDFs/
        └── *.pdf


### 5. Output Format

The final output is written to outputs/collectionname_output.json, containing:

- Input metadata
- Top 5 extracted section summaries
- Full refined content of those top sections

## Pipeline

The pipeline followed by main.py can be broken down into the following stages:


          +------------------+
          |   input.json     |  (with persona, task, and document list)
          +--------+---------+
                   |
                   v
          +--------+---------+
          | Load Persona and |
          | Task Definition  |
          +--------+---------+
                   |
                   v
          +--------+---------+
          |  Generate Goal   |
          |  Statement Text  |
          +--------+---------+
                   |
                   v
          +--------+---------+
          |  Load PDFs from  |
          |   PDFs/ folder   |
          +--------+---------+
                   |
                   v
          +--------+---------+
          | Extract Chunks   |
          | using PyMuPDF    |
          +--------+---------+
                   |
                   v
          +--------+---------+
          | Generate Embeds  |
          | (Goal + Chunks)  |
          +--------+---------+
                   |
                   v
          +--------+---------+
          | Compute Cosine   |
          | Similarity       |
          +--------+---------+
                   |
                   v
          +--------+---------+
          | Select Top 5     |
          | Most Relevant    |
          | Chunks           |
          +--------+---------+
                   |
                   v
          +--------+---------+
          | Create Output    |
          | JSON Structure   |
          +--------+---------+
                   |
                   v
          +------------------+
          |  outputs/*.json  |
          +------------------+



🧠 *Key Idea: The pipeline mimics a simple question-answering or semantic search system, where the user's **task* becomes the query, and PDF content becomes the *search space*.

## Why This Approach?

- *Semantic Matching*: Embedding-based comparison allows for intelligent section extraction based on meaning—not keyword matching.
- *Scalable Design*: Multiple input folders can be processed in a batch, enabling parallelization or pipeline automation.
- *Modular Functions*: extract_pdf_data() and process_collection() isolate logic for clarity and testing.
- *Efficient Inference*: Embeddings and similarity are computed in batch for performance.

## Dependencies Used

- sentence-transformers: For semantic similarity.
- torch: Required backend for sentence transformers.
- PyMuPDF: Fast and accurate PDF parsing.
- tqdm, numpy, pandas, scikit-learn: (if later extended).

## Final Notes

- The script assumes that every input.json references PDFs that are correctly placed in a PDFs/ subfolder.
- If a PDF is missing or unreadable, it is gracefully skipped with a warning.
- The architecture is ready to integrate heading detection or summarization in future updates.