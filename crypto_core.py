"""EmberNote - inti kriptografi.

Satu-satunya algoritma yang dipakai: AES-256-GCM (authenticated encryption).
  - kerahasiaan  : isi pesan dienkripsi (AES-256 mode counter)
  - integritas   : authentication tag 128-bit (GHASH) menolak data yang diubah
  - keaslian metadata : AAD (ID pesan + waktu kedaluwarsa) ikut diautentikasi
Kunci dibuat acak oleh CSPRNG sistem operasi, bukan diturunkan dari password,
sehingga tidak ada algoritma kedua (KDF/hash) di dalam aplikasi.
"""
import base64
import json
import os
import secrets

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_BYTES = 32     # 256 bit
NONCE_BYTES = 12   # 96 bit, ukuran standar GCM


class DecryptionError(Exception):
    """Dekripsi ditolak: kunci salah, ciphertext diubah, atau metadata (AAD) diubah."""


def generate_key() -> bytes:
    """Kunci AES-256 acak (32 byte)."""
    return AESGCM.generate_key(bit_length=256)


def generate_id() -> str:
    """ID pesan acak (bukan rahasia kriptografis, hanya penanda di server)."""
    return secrets.token_urlsafe(12)


def b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def b64_decode(text: str) -> bytes:
    text = text.strip()
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def parse_key(text: str) -> bytes:
    """Ubah teks kunci (Base64 URL-safe) menjadi 32 byte, atau tolak."""
    try:
        key = b64_decode(text)
    except Exception as exc:
        raise DecryptionError("Format kunci tidak valid.") from exc
    if len(key) != KEY_BYTES:
        raise DecryptionError("Format kunci tidak valid.")
    return key


def build_aad(msg_id: str, expires_at: int) -> bytes:
    """Associated Data: metadata yang tidak dienkripsi tetapi ikut diautentikasi."""
    return json.dumps(
        {"id": msg_id, "exp": int(expires_at)}, sort_keys=True, separators=(",", ":")
    ).encode()


def encrypt(plaintext: str, key: bytes, aad: bytes):
    """Return (nonce, ciphertext). Tag 16 byte menempel di akhir ciphertext."""
    if len(key) != KEY_BYTES:
        raise ValueError("Kunci harus 32 byte (AES-256).")
    nonce = os.urandom(NONCE_BYTES)  # nonce baru di setiap enkripsi
    ciphertext = AESGCM(key).encrypt(nonce, plaintext.encode("utf-8"), aad)
    return nonce, ciphertext


def decrypt(nonce: bytes, ciphertext: bytes, key: bytes, aad: bytes) -> str:
    """Dekripsi + verifikasi tag. Jika gagal, tidak ada output sebagian sama sekali."""
    try:
        return AESGCM(key).decrypt(nonce, ciphertext, aad).decode("utf-8")
    except (InvalidTag, ValueError) as exc:
        raise DecryptionError(
            "Kunci salah, atau data/metadata pesan telah diubah (tag GCM tidak cocok)."
        ) from exc
