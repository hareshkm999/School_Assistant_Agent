"""A local, private school-document assistant powered by RAG."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

import chromadb
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from docx import Document
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

APP_DIR = Path(__file__).parent
DB_DIR = APP_DIR / "school_rag_db"
LOGO_PATH = APP_DIR / "assets" / "brigade-logo.png"
COLLECTION_NAME = "school_documents"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SUPPORTED_TYPES = ["pdf", "docx", "txt", "md", "csv", "xlsx"]


@st.cache_resource(show_spinner="Loading the local search model…")
def get_embedder() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


def get_collection():
    """Open a current collection handle.

    Do not cache this object: Streamlit Community Cloud may restart the app
    process or reset the local disk between reruns, which invalidates a cached
    Chroma collection ID.
    """
    client = chromadb.PersistentClient(path=str(DB_DIR))
    return client.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})


def upsert_documents(ids: list[str], documents: list[str], metadatas: list[dict], embeddings: list[list[float]]) -> None:
    """Store passages and recover once if Cloud invalidates a collection handle."""
    try:
        get_collection().upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
    except chromadb.errors.NotFoundError:
        # A Cloud restart can remove the collection after it was opened. Get a
        # new handle and retry the idempotent upsert once.
        get_collection().upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)


def extract_text(uploaded_file) -> str:
    """Extract text from one supported Streamlit uploaded file."""
    extension = uploaded_file.name.rsplit(".", 1)[-1].lower()
    raw = uploaded_file.getvalue()

    if extension == "pdf":
        from io import BytesIO

        return "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(raw)).pages)
    if extension == "docx":
        from io import BytesIO

        return "\n".join(p.text for p in Document(BytesIO(raw)).paragraphs)
    if extension in {"txt", "md"}:
        return raw.decode("utf-8", errors="replace")
    if extension == "csv":
        from io import BytesIO

        return pd.read_csv(BytesIO(raw)).to_csv(index=False)
    if extension == "xlsx":
        from io import BytesIO

        sheets = pd.read_excel(BytesIO(raw), sheet_name=None)
        return "\n\n".join(f"Sheet: {name}\n{frame.to_csv(index=False)}" for name, frame in sheets.items())
    raise ValueError(f"Unsupported file type: {extension}")


def chunk_text(text: str, size: int = 850, overlap: int = 150) -> list[str]:
    """Split text with overlap, preferring paragraph boundaries where possible."""
    normalized = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + size, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind("\n", start, end)
            if boundary > start + size // 2:
                end = boundary
        part = normalized[start:end].strip()
        if part:
            chunks.append(part)
        if end == len(normalized):
            break
        start = max(end - overlap, start + 1)
    return chunks


def index_files(files: Iterable) -> tuple[int, list[str]]:
    embedder = get_embedder()
    documents, metadatas, ids, skipped = [], [], [], []
    for file in files:
        try:
            text = extract_text(file)
            if not text.strip():
                skipped.append(f"{file.name} (no extractable text)")
                continue
            file_hash = hashlib.sha256(file.getvalue()).hexdigest()[:16]
            for number, chunk in enumerate(chunk_text(text)):
                documents.append(chunk)
                metadatas.append({"source": file.name, "chunk": number + 1, "file_hash": file_hash})
                ids.append(f"{file_hash}-{number}")
        except Exception as exc:
            skipped.append(f"{file.name} ({exc})")
    if documents:
        embeddings = get_embedder().encode(documents, normalize_embeddings=True).tolist()
        upsert_documents(ids, documents, metadatas, embeddings)
    return len(documents), skipped


def retrieve(question: str, count: int = 4) -> list[dict]:
    collection = get_collection()
    if collection.count() == 0:
        return []
    vector = get_embedder().encode([question], normalize_embeddings=True).tolist()
    results = collection.query(query_embeddings=vector, n_results=min(count, collection.count()), include=["documents", "metadatas", "distances"])
    return [
        {"text": doc, "source": meta["source"], "chunk": meta["chunk"], "distance": distance}
        for doc, meta, distance in zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
    ]


def build_answer_prompt(question: str, sources: list[dict]) -> str:
    context = "\n\n".join(f"[{i + 1}] {item['text']}" for i, item in enumerate(sources))
    history = st.session_state.get("chat_history", [])[-4:]
    conversation = "\n".join(f"User: {turn['question']}" for turn in history)
    prompt = f"""You are a careful school assistant. Answer using only the supplied school-document context.
If the answer is not present, say that clearly. Do not invent dates, rules, marks, or personal information.
Cite claims using [1], [2], etc. Keep the answer clear and helpful.

Previous questions in this browser session (use only when useful for follow-ups):
{conversation or "None"}

Context:
{context}

Question: {question}
Answer:"""
    return prompt


def show_puter_answer(prompt: str) -> None:
    """Render a Puter.ai request in the visitor's browser.

    Puter handles sign-in in the browser; no API key is stored by this app.
    """
    # Prevent document text from closing the script element in the embedded frame.
    safe_prompt = json.dumps(prompt).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    components.html(
        f"""
        <script src="https://js.puter.com/v2/"></script>
        <style>
          body {{ font-family: sans-serif; margin: 0; color: #262730; line-height: 1.5; }}
          #status {{ color: #555; }}
          #answer p {{ margin: 0 0 0.75rem; }}
          #answer ul, #answer ol {{ margin: 0 0 0.75rem; padding-left: 1.35rem; }}
          #answer h1, #answer h2, #answer h3 {{ margin: 0.75rem 0 0.4rem; }}
        </style>
        <div id="status">Signing in to Puter and preparing an answer…</div>
        <div id="answer"></div>
        <script>
          function escapeHtml(value) {{
            return value.replace(/&/g, '&amp;').replace(/</g, '&lt;')
              .replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
          }}

          function renderMarkdown(value) {{
            const inline = (text) => escapeHtml(text)
              .replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>')
              .replace(/`(.+?)`/g, '<code>$1</code>');
            const lines = value.split(/\\r?\\n/);
            const output = [];
            let listType = null;
            const closeList = () => {{
              if (listType) output.push(`</${{listType}}>`);
              listType = null;
            }};
            for (const line of lines) {{
              const unordered = line.match(/^[-*]\\s+(.+)$/);
              const ordered = line.match(/^\\d+\\.\\s+(.+)$/);
              if (unordered || ordered) {{
                const nextType = unordered ? 'ul' : 'ol';
                if (listType !== nextType) {{ closeList(); output.push(`<${{nextType}}> `); listType = nextType; }}
                output.push(`<li>${{inline((unordered || ordered)[1])}}</li>`);
              }} else {{
                closeList();
                if (!line.trim()) continue;
                const heading = line.match(/^(#{1,3})\\s+(.+)$/);
                if (heading) output.push(`<h${{heading[1].length}}>${{inline(heading[2])}}</h${{heading[1].length}}>`);
                else output.push(`<p>${{inline(line)}}</p>`);
              }}
            }}
            closeList();
            return output.join('');
          }}

          (async () => {{
            const status = document.getElementById('status');
            const answer = document.getElementById('answer');
            try {{
              const reply = await puter.ai.chat({safe_prompt});
              status.remove();
              answer.innerHTML = renderMarkdown(reply.message?.content ?? String(reply));
            }} catch (error) {{
              status.textContent = 'Puter could not generate an answer. Please sign in to Puter in this browser, then ask again.';
              console.error(error);
            }}
          }})();
        </script>
        """,
        height=340,
        scrolling=True,
    )


def clear_library() -> None:
    client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass


st.set_page_config(page_title="Brigade School Assistant Agent", page_icon=str(LOGO_PATH), layout="wide")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

brand, logo = st.columns([6, 1])
with brand:
    st.title("Brigade School Assistant Agent")
    st.caption("Private, local document search and answers. Documents stay on this computer.")
with logo:
    st.image(str(LOGO_PATH), width=100)

with st.sidebar:
    st.image(str(LOGO_PATH), width=130)
    st.subheader("Brigade School Assistant Agent")
    st.header("Document library")
    files = st.file_uploader("Add school documents", type=SUPPORTED_TYPES, accept_multiple_files=True)
    if st.button("Index uploaded documents", type="primary", disabled=not files):
        with st.spinner("Extracting and indexing documents…"):
            count, skipped = index_files(files)
        st.success(f"Added or updated {count} searchable passages.")
        if skipped:
            st.warning("Could not fully index: " + "; ".join(skipped))
    collection = get_collection()
    st.metric("Searchable passages", collection.count())
    if st.button("Start new conversation"):
        st.session_state.chat_history = []
        st.rerun()
    if st.button("Clear document library"):
        clear_library()
        st.rerun()
    st.divider()
    st.caption("Answers are generated with Puter. You may be asked to sign in in the answer panel.")

for turn in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(turn["question"])
    with st.chat_message("assistant"):
        st.caption("Previous response was generated by Puter. Ask a follow-up to continue this session.")

question = st.chat_input("Ask about policies, schedules, curriculum, notices, or other uploaded documents…")
if question:
    sources = retrieve(question)
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        if not sources:
            st.warning("Upload and index at least one document first.")
        else:
            st.caption("Puter will generate the answer below. It may ask you to sign in the first time.")
            show_puter_answer(build_answer_prompt(question, sources))
            with st.expander("Sources used"):
                for index, item in enumerate(sources, start=1):
                    st.markdown(f"**[{index}] {item['source']} — passage {item['chunk']}**")
                    st.write(item["text"])
            st.session_state.chat_history.append({"question": question})
