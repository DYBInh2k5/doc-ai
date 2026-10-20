import os
import re
import secrets
import sqlite3
import base64
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from openai import OpenAI
from pydantic import BaseModel
from pypdf import PdfReader
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "documind.db"
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

JWT_SECRET = os.getenv("JWT_SECRET", "local-development-secret")
JWT_ALGORITHM = "HS256"
bearer = HTTPBearer(auto_error=False)
app = FastAPI(title="Doc AI")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


def init_db():
    with sqlite3.connect(DB_PATH) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                document_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                citations TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (document_id) REFERENCES documents(id)
            );
            """
        )


init_db()


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 240_000)
    return f"pbkdf2_sha256$240000${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, stored_hash: str) -> bool:
    scheme, rounds, encoded_salt, encoded_digest = stored_hash.split("$")
    if scheme != "pbkdf2_sha256":
        return False
    salt = base64.urlsafe_b64decode(encoded_salt.encode())
    expected = base64.urlsafe_b64decode(encoded_digest.encode())
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(rounds))
    return hmac.compare_digest(actual, expected)


class Credentials(BaseModel):
    email: str
    password: str


class Question(BaseModel):
    document_id: int
    question: str


def create_token(user_id: int) -> str:
    expires = datetime.now(timezone.utc) + timedelta(days=7)
    return jwt.encode({"sub": str(user_id), "exp": expires}, JWT_SECRET, algorithm=JWT_ALGORITHM)


def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    db: Annotated[sqlite3.Connection, Depends(get_db)],
):
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Vui long dang nhap")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Phien dang nhap khong hop le")
    user = db.execute("SELECT id, email FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nguoi dung khong ton tai")
    return user


def split_into_chunks(text: str, size: int = 900) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(current) + len(paragraph) > size and current:
            chunks.append(current)
            current = ""
        current += ("\n\n" if current else "") + paragraph
    if current:
        chunks.append(current)
    return chunks or [text[:size]]


def find_relevant_chunks(content: str, question: str) -> list[tuple[int, str]]:
    words = {word.lower() for word in re.findall(r"\w+", question) if len(word) > 2}
    chunks = split_into_chunks(content)
    ranked = []
    for index, chunk in enumerate(chunks, start=1):
        chunk_words = set(re.findall(r"\w+", chunk.lower()))
        score = len(words & chunk_words)
        ranked.append((score, index, chunk))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [(index, chunk) for score, index, chunk in ranked[:3] if score > 0] or [(1, chunks[0])]


def answer_question(question: str, citations: list[tuple[int, str]]) -> str:
    context = "\n\n".join(f"[Doan {index}] {chunk}" for index, chunk in citations)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Chua cau hinh mo hinh AI. Day la cac doan lien quan trong tai lieu:\n\n" + context
    try:
        client_options = {"api_key": api_key}
        base_url = os.getenv("OPENAI_BASE_URL")
        if base_url:
            client_options["base_url"] = base_url
        client = OpenAI(**client_options)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.2,
            messages=[
                {"role": "system", "content": "Tra loi bang tieng Viet, chi dung thong tin trong ngu canh. Neu khong du thong tin, hay noi ro."},
                {"role": "user", "content": f"Ngu canh:\n{context}\n\nCau hoi: {question}"},
            ],
        )
        return response.choices[0].message.content or "Khong co cau tra loi."
    except Exception:
        return "Mo hinh AI dang tam thoi khong phan hoi. Day la cac doan lien quan trong tai lieu:\n\n" + context


@app.get("/")
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/api/auth/register")
def register(credentials: Credentials, db: Annotated[sqlite3.Connection, Depends(get_db)]):
    email = credentials.email.strip().lower()
    if len(credentials.password) < 6:
        raise HTTPException(status_code=400, detail="Mat khau can it nhat 6 ky tu")
    try:
        cursor = db.execute(
            "INSERT INTO users(email, password_hash, created_at) VALUES (?, ?, ?)",
            (email, hash_password(credentials.password), datetime.now(timezone.utc).isoformat()),
        )
        db.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email da ton tai")
    return {"token": create_token(cursor.lastrowid), "email": email}


@app.post("/api/auth/login")
def login(credentials: Credentials, db: Annotated[sqlite3.Connection, Depends(get_db)]):
    user = db.execute("SELECT * FROM users WHERE email = ?", (credentials.email.strip().lower(),)).fetchone()
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email hoac mat khau khong dung")
    return {"token": create_token(user["id"]), "email": user["email"]}


@app.get("/api/documents")
def documents(user=Depends(current_user), db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute("SELECT id, filename, created_at FROM documents WHERE user_id = ? ORDER BY id DESC", (user["id"],)).fetchall()
    return [dict(row) for row in rows]


@app.post("/api/documents")
def upload_document(file: UploadFile = File(...), user=Depends(current_user), db: sqlite3.Connection = Depends(get_db)):
    extension = Path(file.filename or "").suffix.lower()
    if extension not in {".pdf", ".txt"}:
        raise HTTPException(status_code=400, detail="Chi ho tro file PDF va TXT")
    raw = file.file.read()
    try:
        if extension == ".pdf":
            stored_path = UPLOAD_DIR / f"{secrets.token_hex(12)}.pdf"
            stored_path.write_bytes(raw)
            content = "\n\n".join(page.extract_text() or "" for page in PdfReader(stored_path).pages)
        else:
            content = raw.decode("utf-8")
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"Khong doc duoc file: {error}")
    if not content.strip():
        raise HTTPException(status_code=400, detail="File khong co noi dung van ban")
    cursor = db.execute(
        "INSERT INTO documents(user_id, filename, content, created_at) VALUES (?, ?, ?, ?)",
        (user["id"], file.filename, content, datetime.now(timezone.utc).isoformat()),
    )
    db.commit()
    return {"id": cursor.lastrowid, "filename": file.filename}


@app.post("/api/chat")
def chat(payload: Question, user=Depends(current_user), db: sqlite3.Connection = Depends(get_db)):
    document = db.execute("SELECT * FROM documents WHERE id = ? AND user_id = ?", (payload.document_id, user["id"])).fetchone()
    if not document:
        raise HTTPException(status_code=404, detail="Tai lieu khong ton tai")
    citations = find_relevant_chunks(document["content"], payload.question)
    answer = answer_question(payload.question, citations)
    db.execute(
        "INSERT INTO messages(user_id, document_id, question, answer, citations, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (user["id"], document["id"], payload.question, answer, "|".join(str(index) for index, _ in citations), datetime.now(timezone.utc).isoformat()),
    )
    db.commit()
    return {"answer": answer, "citations": [{"section": index, "text": chunk} for index, chunk in citations]}


@app.get("/api/history")
def history(user=Depends(current_user), db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute(
        "SELECT messages.*, documents.filename FROM messages JOIN documents ON documents.id = messages.document_id WHERE messages.user_id = ? ORDER BY messages.id DESC LIMIT 50",
        (user["id"],),
    ).fetchall()
    return [dict(row) for row in rows]
