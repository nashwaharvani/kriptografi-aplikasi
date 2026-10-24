"""Penyimpanan server (SQLite). Server HANYA menyimpan ciphertext, tidak pernah kunci/plaintext."""
import sqlite3
import time
from contextlib import closing

DB_PATH = "embernote.db"


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=10, isolation_level=None)  # autocommit
    conn.execute(
        """CREATE TABLE IF NOT EXISTS messages (
               id TEXT PRIMARY KEY,
               nonce BLOB NOT NULL,
               ciphertext BLOB NOT NULL,
               expires_at INTEGER NOT NULL,
               created_at INTEGER NOT NULL
           )"""
    )
    conn.execute("DELETE FROM messages WHERE expires_at <= ?", (int(time.time()),))
    return conn


def save_message(msg_id, nonce, ciphertext, expires_at, db_path=DB_PATH) -> None:
    with closing(_connect(db_path)) as conn:
        conn.execute(
            "INSERT INTO messages VALUES (?, ?, ?, ?, ?)",
            (msg_id, nonce, ciphertext, int(expires_at), int(time.time())),
        )


def fetch_message(msg_id, db_path=DB_PATH):
    """Ambil pesan (tanpa menghapus). None jika tidak ada / sudah kedaluwarsa."""
    with closing(_connect(db_path)) as conn:
        row = conn.execute(
            "SELECT id, nonce, ciphertext, expires_at, created_at FROM messages WHERE id = ?",
            (msg_id,),
        ).fetchone()
    if row is None:
        return None
    return {
        "id": row[0], "nonce": row[1], "ciphertext": row[2],
        "expires_at": row[3], "created_at": row[4],
    }


def consume_message(msg_id, db_path=DB_PATH) -> bool:
    """Hapus pesan secara atomik. True hanya untuk SATU pemanggil yang berhasil menghapus."""
    with closing(_connect(db_path)) as conn:
        return conn.execute("DELETE FROM messages WHERE id = ?", (msg_id,)).rowcount == 1
