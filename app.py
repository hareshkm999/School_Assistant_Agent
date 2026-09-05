"""A local, private school-document assistant powered by RAG."""

from __future__ import annotations

import hashlib
import json
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Iterable

import chromadb
import pandas as pd
import pytesseract
import streamlit as st
import streamlit.components.v1 as components
from docx import Document
from PIL import Image
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

APP_DIR = Path(__file__).parent
DB_DIR = APP_DIR / "school_rag_db"
LOGO_PATH = APP_DIR / "assets" / "brigade-logo.png"
COLLECTION_NAME = "school_documents"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SUPPORTED_TYPES = ["pdf", "docx", "txt", "md", "csv", "xlsx", "png", "jpg", "jpeg"]
INTRODUCTION_ANSWER = (
    "I am **Sia**, the school's **Academic AI Assistant**. I help students understand uploaded school "
    "documents such as study material, circulars, schedules, handbooks, and notices. You can ask me "
    "questions in simple language, and I will provide clear answers using the relevant document sources.\n\n"
    "I was developed by **Shannavi Shree Eeshta** from **Brigade Public School, Attapur**, and launched on "
    "**September 3, 2026**."
)
SIA_SYSTEM_PROMPT = """You are Sia, the Academic AI Assistant for Brigade Public School, Attapur.
Your audience is primarily Grade 7 students, parents, and teachers. Use warm, clear, age-appropriate language.
Answer school-information questions using only the supplied document context. Never invent names, dates, marks,
fees, percentages, policies, or personal information. Do not include citation markers such as [1] or [2] in the
visible answer; users can open the separate Sources used panel to verify the information.
Lead with what the documents confirm. If an exact requested detail is missing, say what is confirmed and state that
the exact detail is not stated in the provided material; suggest a useful next step such as checking the school
office, teacher, or official result sheet. Do not use dismissive wording such as 'I can't' or 'I don't know'.
Encourage safe, independent learning and recommend a teacher or parent for important decisions. Use plain text
mathematics such as "7 x 7 x 7 = 343". Do not use LaTeX commands, backslash delimiters, or markdown heading symbols.
For a short follow-up such as "draw a diagram", "explain it", "give examples", or "summarize it", identify the
topic from the immediately previous conversation and keep the response on that topic. Do not replace it with an
unrelated result from another school document. When asked to draw a diagram, provide a clear labelled ASCII/text
diagram that a student can copy into a notebook, followed by a short explanation."""


@st.cache_resource(show_spinner="Loading the local search model…")
def get_embedder() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


def get_collection():
    """Open a current collection handle.

    Use Chroma Cloud when all deployment secrets are configured. Otherwise,
    keep local development simple by using the on-disk Chroma database.
    """
    try:
        client = chromadb.CloudClient(
            api_key=st.secrets["CHROMA_API_KEY"],
            tenant=st.secrets["CHROMA_TENANT"],
            database=st.secrets["CHROMA_DATABASE"],
        )
    except Exception:
        client = chromadb.PersistentClient(path=str(DB_DIR))
    return client.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})


def get_chroma_client():
    """Return the same local-or-cloud client used by the collection helper."""
    try:
        return chromadb.CloudClient(
            api_key=st.secrets["CHROMA_API_KEY"],
            tenant=st.secrets["CHROMA_TENANT"],
            database=st.secrets["CHROMA_DATABASE"],
        )
    except Exception:
        return chromadb.PersistentClient(path=str(DB_DIR))


def upsert_documents(ids: list[str], documents: list[str], metadatas: list[dict], embeddings: list[list[float]]) -> None:
    """Store passages and recover once if Cloud invalidates a collection handle."""
    try:
        get_collection().upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
    except chromadb.errors.NotFoundError:
        # A Cloud restart can remove the collection after it was opened. Get a
        # new handle and retry the idempotent upsert once.
        get_collection().upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)


def ocr_image(image_bytes: bytes) -> str:
    """Extract text from an image with the locally installed Tesseract engine."""
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        return pytesseract.image_to_string(image).strip()
    except pytesseract.TesseractNotFoundError as exc:
        raise RuntimeError("Tesseract OCR is not installed. Install Tesseract, then restart Sia.") from exc


def ocr_scanned_pdf(raw: bytes) -> str:
    """Render a scanned PDF page-by-page and extract its visible text."""
    try:
        import fitz  # PyMuPDF

        pdf = fitz.open(stream=raw, filetype="pdf")
        text = []
        for page in pdf:
            image = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            text.append(ocr_image(image.tobytes("png")))
        return "\n".join(part for part in text if part)
    except pytesseract.TesseractNotFoundError:
        raise


def extract_docx_images(raw: bytes) -> str:
    """OCR images embedded in a Word document."""
    image_text = []
    with zipfile.ZipFile(BytesIO(raw)) as archive:
        for name in archive.namelist():
            if name.startswith("word/media/"):
                try:
                    extracted = ocr_image(archive.read(name))
                    if extracted:
                        image_text.append(extracted)
                except (OSError, ValueError):
                    # Some Word files contain unsupported vector media; keep
                    # indexing the document's normal text and other images.
                    continue
    return "\n".join(image_text)


def extract_text(uploaded_file) -> str:
    """Extract text from one supported Streamlit uploaded file."""
    extension = uploaded_file.name.rsplit(".", 1)[-1].lower()
    raw = uploaded_file.getvalue()

    if extension == "pdf":
        extracted = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(raw)).pages)
        # Use OCR only where PDF text is absent: avoids duplicating text in digital PDFs.
        return extracted if extracted.strip() else ocr_scanned_pdf(raw)
    if extension == "docx":
        document_text = "\n".join(p.text for p in Document(BytesIO(raw)).paragraphs)
        embedded_image_text = extract_docx_images(raw)
        return "\n".join(part for part in [document_text, embedded_image_text] if part)
    if extension in {"txt", "md"}:
        return raw.decode("utf-8", errors="replace")
    if extension == "csv":
        return pd.read_csv(BytesIO(raw)).to_csv(index=False)
    if extension == "xlsx":
        sheets = pd.read_excel(BytesIO(raw), sheet_name=None)
        return "\n\n".join(f"Sheet: {name}\n{frame.to_csv(index=False)}" for name, frame in sheets.items())
    if extension in {"png", "jpg", "jpeg"}:
        return ocr_image(raw)
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


def is_short_follow_up(question: str) -> bool:
    """Recognize commands that rely on the topic from the previous turn."""
    normalized = question.strip().lower().rstrip("?.!")
    follow_up_starts = ("draw", "can draw", "can you draw", "show", "explain it", "summarize it", "give example", "give examples", "make a")
    return len(normalized.split()) <= 8 and normalized.startswith(follow_up_starts)


def build_answer_prompt(question: str, sources: list[dict]) -> str:
    context = "\n\n".join(f"[{i + 1}] {item['text']}" for i, item in enumerate(sources))
    history = st.session_state.get("chat_history", [])[-3:]
    history_items = []
    for turn in history:
        item = f"Earlier user question: {turn['question']}"
        if turn.get("answer"):
            item += f"\nEarlier Sia response: {turn['answer']}"
        elif turn.get("sources"):
            excerpts = "\n".join(
                f"- {source['source']}: {source['text'][:550]}"
                for source in turn["sources"][:2]
            )
            item += f"\nRelevant extracts used for the earlier answer:\n{excerpts}"
        history_items.append(item)
    conversation = "\n\n".join(history_items)
    prompt = f"""SYSTEM INSTRUCTIONS (follow these throughout your response):
{SIA_SYSTEM_PROMPT}

Relevant earlier conversation and source extracts (use only when useful for follow-ups):
{conversation or "None"}

Context:
{context}

Question: {question}
Answer:"""
    return prompt


def show_puter_answer(prompt: str, response_key: str) -> None:
    """Render a Puter.ai request in the visitor's browser.

    Puter handles sign-in in the browser; no API key is stored by this app.
    """
    # Prevent document text from closing the script element in the embedded frame.
    safe_prompt = json.dumps(prompt).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    safe_key = json.dumps(f"sia-answer-{response_key}")
    components.html(
        f"""
        <script src="https://js.puter.com/v2/"></script>
        <style>
          body {{
            background: #0e1117;
            box-sizing: border-box;
            color: #f7f9fc;
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0 2px;
          }}
          #status {{ color: #b8c0cd; font-weight: 600; }}
          #answer {{ color: #f7f9fc; font-size: 1rem; max-height: 250px; overflow-y: auto; padding-right: 10px; }}
          #answer p {{ color: #f7f9fc; margin: 0 0 0.8rem; }}
          #answer strong {{ color: #ffffff; }}
          #answer ul, #answer ol {{ color: #f7f9fc; margin: 0 0 0.85rem; padding-left: 1.45rem; }}
          #answer li {{ color: #f7f9fc; margin-bottom: 0.35rem; }}
          #answer h1, #answer h2, #answer h3 {{ color: #ffffff; margin: 0.75rem 0 0.4rem; }}
          #answer code {{ background: #1d2430; border-radius: 4px; color: #ffffff; padding: 0.1rem 0.25rem; }}
        </style>
        <div id="status">Signing in to Puter and preparing an answer…</div>
        <div id="answer"></div>
        <script>
          const MIN_FRAME_HEIGHT = 120;
          const MAX_FRAME_HEIGHT = 540;

          function resizeFrame() {{
            const status = document.getElementById('status');
            const answer = document.getElementById('answer');
            const contentHeight = (status ? status.scrollHeight : 0) + answer.scrollHeight + 42;
            const height = Math.min(MAX_FRAME_HEIGHT, Math.max(MIN_FRAME_HEIGHT, contentHeight));
            const message = {{
              isStreamlitMessage: true,
              type: 'streamlit:setFrameHeight',
              height: height,
            }};
            window.parent.postMessage(message, '*');
            if (window.top !== window.parent) window.top.postMessage(message, '*');
          }}

          new ResizeObserver(resizeFrame).observe(document.getElementById('answer'));

          function escapeHtml(value) {{
            return value.replace(/&/g, '&amp;').replace(/</g, '&lt;')
              .replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
          }}

          function renderMarkdown(value) {{
            const slash = String.fromCharCode(92);
            const cleanText = value
              .replace(/[[][0-9, ]+[]]/g, '')
              .split(slash + '[').join('').split(slash + ']').join('')
              .split(slash + '(').join('').split(slash + ')').join('')
              .split(slash + 'times').join('×').split(slash + 'cdot').join('·');
            const inline = (text) => escapeHtml(text)
              .replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>')
              .replace(/\\*(.+?)\\*/g, '$1')
              .replace(/`(.+?)`/g, '<code>$1</code>');
            const lines = cleanText.split(/\\r?\\n/);
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
              const cachedAnswer = window.localStorage.getItem({safe_key});
              if (cachedAnswer) {{
                status.remove();
                answer.innerHTML = renderMarkdown(cachedAnswer);
                resizeFrame();
                return;
              }}
              const reply = await puter.ai.chat({safe_prompt});
              const answerText = reply.message?.content ?? String(reply);
              window.localStorage.setItem({safe_key}, answerText);
              status.remove();
              answer.innerHTML = renderMarkdown(answerText);
              resizeFrame();
            }} catch (error) {{
              status.textContent = 'Puter could not generate an answer. Please sign in to Puter in this browser, then ask again.';
              resizeFrame();
              console.error(error);
            }}
          }})();
        </script>
        """,
        # Streamlit's embedded HTML frame does not consistently honor dynamic
        # height messages in every browser. Use a comfortable fixed viewport
        # with scroll support so no answer text is hidden.
        height=200,
        scrolling=True,
    )


def clear_library() -> None:
    client = get_chroma_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass


def render_saved_turn(turn: dict) -> None:
    """Render conversation state retained for this browser session."""
    with st.chat_message("user"):
        st.write(turn["question"])
    with st.chat_message("assistant"):
        if turn.get("answer"):
            st.markdown(turn["answer"])
        elif turn.get("puter_prompt"):
            show_puter_answer(turn["puter_prompt"], turn["response_key"])
        elif turn.get("sources"):
            st.info("Sia answered this question using the saved document sources below. Ask a follow-up to continue the discussion.")
            with st.expander("Sources used"):
                for index, item in enumerate(turn["sources"], start=1):
                    st.markdown(f"**[{index}] {item['source']} - passage {item['chunk']}**")
                    st.write(item["text"])


st.set_page_config(page_title="Brigade School Intelligent Agent", page_icon=str(LOGO_PATH), layout="wide")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

logo, brand = st.columns([1, 6], vertical_alignment="center")
with logo:
    st.image(str(LOGO_PATH), width=82)
with brand:
    st.title("Meet Sia")
    st.caption("Private, local document search and answers. Documents stay on this computer.")

with st.sidebar:
    st.image(str(LOGO_PATH), width=130)
    st.subheader("Meet Sia")
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

# Keep the five most recent questions and answers visible in this browser session.
for turn in st.session_state.chat_history[-5:]:
    render_saved_turn(turn)

question = st.chat_input("Ask about policies, schedules, curriculum, notices, or other uploaded documents…")
if question:
    normalized_question = question.strip().lower().rstrip("?.!")
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        if normalized_question in {
            "who are you", "what are you", "tell me about yourself", "tell me about sia", "what is sia",
            "who created you", "who made you", "who developed you", "who is your creator", "who built you",
        }:
            st.markdown(INTRODUCTION_ANSWER)
            st.session_state.chat_history.append({"question": question, "answer": INTRODUCTION_ANSWER})
        else:
            previous_turn = st.session_state.chat_history[-1] if st.session_state.chat_history else {}
            if is_short_follow_up(question) and previous_turn.get("sources"):
                # Short requests like "draw a diagram" should stay on the
                # prior lesson instead of retrieving an unrelated document.
                sources = previous_turn["sources"]
            else:
                sources = retrieve(question)
            if not sources:
                answer = "Please upload and index an approved school document first, then I can help you find the answer."
                st.warning(answer)
                st.session_state.chat_history.append({"question": question, "answer": answer})
            else:
                st.caption("Puter will generate the answer below. It may ask you to sign in the first time.")
                puter_prompt = build_answer_prompt(question, sources)
                response_key = hashlib.sha256(f"{len(st.session_state.chat_history)}:{puter_prompt}".encode()).hexdigest()[:20]
                show_puter_answer(puter_prompt, response_key)
                with st.expander("Sources used"):
                    for index, item in enumerate(sources, start=1):
                        st.markdown(f"**[{index}] {item['source']} — passage {item['chunk']}**")
                        st.write(item["text"])
                st.session_state.chat_history.append(
                    {
                        "question": question,
                        "sources": sources,
                        "puter_prompt": puter_prompt,
                        "response_key": response_key,
                    }
                )
