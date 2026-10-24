# EmberNote 🔥
Aplikasi pesan rahasia sekali baca (burn-after-reading) berbasis **AES-256-GCM**, satu algoritma saja.

## Struktur
```
EmberNote/
├── .streamlit/
│   └── config.toml      # tema warna Streamlit
├── images/
│   └── logo.png         # logo; taruh screenshot laporan (jpg) di sini
├── modules/
│   ├── __init__.py
│   ├── aes_gcm.py       # inti kriptografi: AES-256-GCM + AAD
│   ├── storage.py       # penyimpanan SQLite (hanya ciphertext)
│   └── selftest.py      # 9 pengujian otomatis (bukti keamanan)
├── .gitignore
├── app.py               # aplikasi Streamlit (4 halaman)
├── tema.py              # CSS dan komponen tampilan
├── laporan.ipynb        # notebook laporan: penjelasan, kode, pengujian, demo
├── README.md
└── requirements.txt
```

## Menjalankan lokal
```bash
pip install -r requirements.txt
streamlit run app.py
python -m modules.selftest     # opsional: jalankan 9 pengujian di terminal
```

## Deploy ke Streamlit Community Cloud
1. Upload seluruh isi folder ini ke repository GitHub (`.gitignore` sudah menyingkirkan file yang tidak perlu).
2. Buka https://share.streamlit.io, login dengan GitHub, klik **Create app**.
3. Pilih repository dan branch, isi **Main file path** dengan `app.py`, lalu **Deploy**.

Catatan: penyimpanan di Streamlit Cloud bersifat sementara; file `embernote.db` hilang saat aplikasi restart.

## Alur singkat
1. **Buat Pesan**: pesan dienkripsi dengan kunci acak 256-bit, server menyimpan nonce + ciphertext.
2. Bagikan **ID** dan **kunci** lewat dua jalur berbeda.
3. **Baca Pesan**: dekripsi + verifikasi tag, lalu pesan dihapus (hanya satu pembaca yang berhasil).

## Batasan dan ancaman yang tidak ditangani
- Bukan E2EE murni: kunci dibuat dan dipakai di server saat pesan dibuat/dibuka.
- Siapa pun yang memegang ID + kunci dapat membuka pesan.
- Panjang pesan, ID, dan waktu dibuat/kedaluwarsa tidak tersembunyi.
- Tidak ada pembatasan spam atau percobaan.
- Penyimpanan Streamlit Cloud sementara; plaintext tetap ada di sesi browser sampai pesan ditutup.
- Proyek pembelajaran, belum diaudit pihak independen.
