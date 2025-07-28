# PDF Semantic Extractor

This project processes PDF documents to extract the *most relevant sections* based on a given *user persona* and a *task objective* using semantic similarity. It's packaged in a Docker container and is ready for evaluation with standardized input and output directories.

---

## Features

- Uses SentenceTransformer (all-MiniLM-L6-v2) for semantic similarity.
- Extracts meaningful text blocks from PDFs using PyMuPDF.
- Ranks the most relevant sections according to user context (persona and job_to_be_done).
- Outputs results in structured JSON format.

---

## Docker Usage

### 1. Build the Docker Image

bash
docker build -t hackathon_solution


### 2. Run the Container

bash
docker run --rm \\
  -v $(pwd)/input:/app/inputs \\
  -v $(pwd)/output:/app/outputs \\
  --network none \\
  mysolutionname:somerandomidentifier



- input/: Should contain subfolders for each collection.
- output/: Will contain one _output.json file for each collection processed.

---

## Input Folder Structure


input/
└── collection_1/
    ├── input.json
    └── PDFs/
        ├── doc1.pdf
        └── doc2.pdf
└── collection_2/
    ├── input.json
    └── PDFs/
        └── ...



### input.json Format

json
{
  "persona": { "role": "student" },
  "job_to_be_done": { "task": "prepare for an exam" },
  "documents": [
    { "filename": "doc1.pdf" },
    { "filename": "doc2.pdf" }
  ]
}



## Output Format

Each collection generates an output file named collectionname_output.json under the /output directory.

### Example

json
{
  "metadata": {
    "input_documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "student",
    "job_to_be_done": "prepare for an exam",
    "processing_timestamp": "2025-07-28T12:00:00"
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "section_title": "What is Reinforcement Learning...",
      "importance_rank": 1,
      "page_number": 3
    }
  ],
  "subsection_analysis": [
    {
      "document": "doc1.pdf",
      "refined_text": "Reinforcement learning is a feedback-driven...",
      "page_number": 3
    }
  ]
}



## Tech Stack

- Python 3.10
- PyMuPDF
- SentenceTransformers
- Torch (CPU)
- Docker

## Notes

- No internet access is allowed inside the container (-network none).
- Make sure all required PDFs and input.json are placed correctly before running.
