
# ingest.py — build vector store with LangChain (OpenAI embeddings + FAISS)
import os, re, io
from typing import List, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from pypdf import PdfReader
from docx import Document as DocxDocument

def _read_pdf(file) -> str:
    reader = PdfReader(file)
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            pass
    return "\n".join(texts)

def _read_docx(file) -> str:
    doc = DocxDocument(file)
    texts = [p.text for p in doc.paragraphs]
    return "\n".join(texts)

def _read_text(file) -> str:
    content = file.read()
    try:
        return content.decode("utf-8")
    except Exception:
        return content.decode("latin-1", errors="ignore")

def _chunk(text: str, chunk_size=800, overlap=200) -> List[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.split_text(text)

def build_vectorstore_from_uploads(files):
    """Returns: (vectorstore, retriever, docs_meta)"""
    documents, metas = [], []
    # Need to read file bytes twice; buffer into memory
    buffered = []
    for f in files:
        data = f.read()
        buffered.append((f.name, data))
    for name, data in buffered:
        import io as _io
        ext = os.path.splitext(name)[1].lower()
        if ext == ".pdf":
            text = _read_pdf(_io.BytesIO(data))
        elif ext == ".docx":
            text = _read_docx(_io.BytesIO(data))
        else:
            text = _read_text(_io.BytesIO(data))
        chunks = _chunk(text)
        for c in chunks:
            documents.append(c)
            metas.append({"source": name})
    if not documents:
        raise RuntimeError("No content extracted from uploads.")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vs = FAISS.from_texts(documents, embedding=embeddings, metadatas=metas)
    retriever = vs.as_retriever(search_kwargs={"k": 5})

    # compute meta table
    docs_meta = []
    for name, data in buffered:
        import io as _io
        ext = os.path.splitext(name)[1].lower()
        if ext == ".pdf":
            text = _read_pdf(_io.BytesIO(data))
        elif ext == ".docx":
            text = _read_docx(_io.BytesIO(data))
        else:
            text = _read_text(_io.BytesIO(data))
        docs_meta.append({"file": name, "chars": len(text), "chunks": len(_chunk(text))})
    return vs, retriever, docs_meta
