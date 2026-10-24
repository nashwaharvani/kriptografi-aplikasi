"""Pengujian otomatis sebagai BUKTI bahwa satu algoritma (AES-256-GCM) sudah cukup."""
import os
import sqlite3
import tempfile
import time

from . import aes_gcm as cc
from . import storage


def _rejected(func) -> bool:
    try:
        func()
    except cc.DecryptionError:
        return True
    return False


def run_all():
    results = []

    def check(name, ok, detail):
        results.append({"Pengujian": name, "Hasil": "LULUS" if ok else "GAGAL", "Keterangan": detail})

    key = cc.generate_key()
    msg_id = cc.generate_id()
    exp = int(time.time()) + 3600
    aad = cc.build_aad(msg_id, exp)
    plain = "Pesan rahasia uji EmberNote"
    nonce, ct = cc.encrypt(plain, key, aad)

    check("1. Round-trip", cc.decrypt(nonce, ct, key, aad) == plain,
          "Enkripsi lalu dekripsi menghasilkan teks yang sama persis.")

    check("2. Kunci salah ditolak", _rejected(lambda: cc.decrypt(nonce, ct, cc.generate_key(), aad)),
          "Tidak ada output sebagian, dekripsi gagal total.")

    bad = bytearray(ct); bad[0] ^= 0x01
    check("3. Ciphertext diubah 1 bit", _rejected(lambda: cc.decrypt(nonce, bytes(bad), key, aad)),
          "Tag GCM mendeteksi perubahan, tanpa perlu hash/MAC tambahan.")

    bad = bytearray(ct); bad[-1] ^= 0x01
    check("4. Tag diubah", _rejected(lambda: cc.decrypt(nonce, bytes(bad), key, aad)),
          "Authentication tag yang dipalsukan ditolak.")

    check("5. Metadata (AAD) diubah", _rejected(
        lambda: cc.decrypt(nonce, ct, key, cc.build_aad(msg_id, exp + 86400))),
        "Memperpanjang waktu kedaluwarsa pesan membuat dekripsi gagal.")

    n2, ct2 = cc.encrypt(plain, key, aad)
    check("6. Nonce unik", nonce != n2 and ct != ct2,
          "Plaintext sama dienkripsi dua kali menghasilkan ciphertext berbeda.")

    check("7. Plaintext tidak bocor", plain.encode() not in ct,
          "Teks asli tidak muncul di dalam ciphertext yang disimpan.")

    with tempfile.TemporaryDirectory() as tmp:
        db = os.path.join(tmp, "test.db")
        storage.save_message(msg_id, nonce, ct, exp, db)
        first = storage.consume_message(msg_id, db)
        second = storage.consume_message(msg_id, db)
        check("8. Sekali baca", first and not second and storage.fetch_message(msg_id, db) is None,
              "Pembaca pertama berhasil menghapus, pembaca kedua tidak mendapat apa-apa.")

        storage.save_message("kadaluwarsa", nonce, ct, int(time.time()) + 1, db)
        sqlite3.connect(db).execute("UPDATE messages SET expires_at = ?", (int(time.time()) - 1,)).connection.commit()
        check("9. Kedaluwarsa", storage.fetch_message("kadaluwarsa", db) is None,
              "Pesan yang melewati masa berlaku otomatis terhapus.")

    return results


# Jalankan: python -m modules.selftest
if __name__ == "__main__":
    for r in run_all():
        print(f"{r['Hasil']:6} {r['Pengujian']:32} {r['Keterangan']}")
