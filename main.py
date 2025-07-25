import os
import json
import fitz  # PyMuPDF
from datetime import datetime
from sentence_transformers import SentenceTransformer, util
from pathlib import Path

# Load model once
model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_pdf_data(pdf_path):
    doc = fitz.open(pdf_path)
    title = os.path.splitext(os.path.basename(pdf_path))[0]
    results = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            text = " ".join([span["text"] for line in block["lines"] for span in line["spans"]]).strip()
            if len(text) < 10:
                continue
            results.append({
                "title": title,
                "page": page_num + 1,
                "text": text
            })
    return results

def process_collection(collection_path: Path, output_dir: Path):
    input_json_path = collection_path / "input.json"
    pdf_dir = collection_path / "PDFs"

    if not input_json_path.exists():
        print(f"Missing input.json in {collection_path}")
        return

    with open(input_json_path, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    persona = input_data["persona"]["role"]
    job_to_be_done = input_data["job_to_be_done"]["task"]
    goal_text = f"As a {persona}, I need to {job_to_be_done}. Find the most relevant sections that help with this task."

    pdf_filenames = [doc["filename"] for doc in input_data["documents"]]
    all_chunks = []

    for filename in pdf_filenames:
        pdf_path = pdf_dir / filename
        if not pdf_path.exists():
            print(f"PDF not found: {pdf_path}")
            continue
        chunks = extract_pdf_data(str(pdf_path))
        all_chunks.extend(chunks)

    # Compute similarity
    goal_emb = model.encode(goal_text, convert_to_tensor=True)
    texts = [chunk["text"] for chunk in all_chunks]
    text_embs = model.encode(texts, convert_to_tensor=True)

    sims = util.cos_sim(goal_emb, text_embs)[0]
    top_indices = sims.argsort(descending=True)[:5]

    top_chunks = []
    for rank, idx in enumerate(top_indices, 1):
        chunk = all_chunks[int(idx)]
        top_chunks.append({
            "document": chunk["title"] + ".pdf",
            "section_title": chunk["text"][:70] + "...",
            "importance_rank": rank,
            "page_number": chunk["page"],
            "refined_text": chunk["text"]
        })

    output_data = {
        "metadata": {
            "input_documents": pdf_filenames,
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [
            {
                "document": chunk["document"],
                "section_title": chunk["section_title"],
                "importance_rank": chunk["importance_rank"],
                "page_number": chunk["page_number"]
            } for chunk in top_chunks
        ],
        "subsection_analysis": [
            {
                "document": chunk["document"],
                "refined_text": chunk["refined_text"],
                "page_number": chunk["page_number"]
            } for chunk in top_chunks
        ]
    }

    output_filename = f"{collection_path.name}_output.json"
    output_path = output_dir / output_filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)
    print(f"Saved: {output_path}")

def main():
    input_root = Path("inputs")
    output_root = Path("outputs")
    output_root.mkdir(exist_ok=True)

    collections = [p for p in input_root.iterdir() if p.is_dir()]
    if not collections:
        print("No input folders found.")
        return

    for collection_path in collections:
        print(f"Processing collection: {collection_path.name}")
        process_collection(collection_path, output_root)

if __name__ == "__main__":
    main()
