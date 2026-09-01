# School Assistant (local RAG)

A simple private assistant for school policies, circulars, schedules, curriculum documents, and spreadsheets. It runs on your computer with open-source tools:

- **Streamlit** for the web interface
- **sentence-transformers** (`all-MiniLM-L6-v2`) for local semantic search
- **ChromaDB** for a local vector database
- **Puter AI** for answer generation in the browser (sign-in may be required)

## Setup

1. Install [Python 3.10+](https://www.python.org/downloads/).
2. In this folder, create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. Start the app:

   ```powershell
   streamlit run app.py
   ```

## Use

Upload PDF, DOCX, TXT, Markdown, CSV, or XLSX files from the sidebar, select **Index uploaded documents**, then ask a question. Every response exposes the source passages used so staff can check it.

The local vector library is stored in `school_rag_db/`. Use **Clear document library** to remove it. Scanned PDFs need OCR before they can be searched; this app indexes embedded PDF text.

## Privacy notes

The document library and search embeddings remain local. To generate each response, the selected source passages and your question are sent from the browser to Puter AI. Apply your school’s access-control and data-retention policies, obtain appropriate authorization, and do not upload documents from people who have not authorized their use.
