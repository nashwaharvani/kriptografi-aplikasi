# EmberNote 🔥
Aplikasi pesan rahasia sekali baca (burn-after-reading) berbasis **AES-256-GCM** (satu algoritma saja).

## Struktur
```
EmberNote/
├── EmberNote.ipynb     # notebook lengkap: penjelasan, kode, pengujian, demo
├── app.py              # aplikasi Streamlit
├── crypto_core.py      # inti kriptografi (AES-256-GCM + AAD)
├── storage.py          # penyimpanan SQLite (hanya ciphertext)
├── selftest.py         # pengujian otomatis (bukti keamanan)
├── requirements.txt
└── README.md
```

## Menjalankan lokal
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy ke Streamlit Community Cloud
1. Upload `app.py`, `crypto_core.py`, `storage.py`, `selftest.py`, `requirements.txt` ke repository GitHub (publik atau privat).
2. Buka https://share.streamlit.io, login dengan GitHub, klik **Create app**.
3. Pilih repository, branch, dan isi **Main file path** dengan `app.py`, lalu **Deploy**.

Catatan: penyimpanan di Streamlit Cloud bersifat sementara (file `embernote.db` hilang saat aplikasi restart), yang justru sesuai untuk pesan yang memang sementara.

## Alur singkat
1. **Buat Pesan**: pesan dienkripsi dengan kunci acak 256-bit, server menyimpan nonce + ciphertext.
2. Bagikan **ID** dan **kunci** lewat dua jalur berbeda.
3. **Baca Pesan**: dekripsi + verifikasi tag, lalu pesan dihapus (hanya satu pembaca yang berhasil).
