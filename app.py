"""EmberNote - Pesan rahasia sekali baca berbasis AES-256-GCM (Streamlit Neo-Brutalist)."""
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import streamlit as st

import tema
from modules import aes_gcm as cc
from modules import selftest, storage

st.set_page_config(page_title="EmberNote", page_icon="🔥", layout="wide")
tema.apply_theme()

MAX_CHARS = 5000
DURATIONS = {"5 menit": 300, "1 jam": 3600, "24 jam": 86400, "7 hari": 604800}
PAGES = ["🔥 Buat Pesan", "📖 Baca Pesan", "🛡️ Bukti Keamanan", "ℹ️ Tentang"]
WIB = timezone(timedelta(hours=7))


def fmt_time(ts: int) -> str:
    return datetime.fromtimestamp(ts, WIB).strftime("%d %b %Y %H:%M:%S WIB")


# ---------------------------------------------------------------- Buat pesan
def page_create():
    col_main, col_side = st.columns([7, 5])

    with col_main:
        tema.page_header("Buat Pesan", "Pesan dienkripsi dengan AES-256-GCM, dibuka sekali, lalu hangus.")
        tema.hero(
            "EmberNote",
            "Aplikasi pesan rahasia sekali baca (burn-after-reading). Diuji membuktikan satu cipher AES-256-GCM mencukupi tanpa MAC/hash tambahan.",
        )

        with st.form("form_buat", clear_on_submit=True):
            text = st.text_area("Tulis pesan rahasiamu", max_chars=MAX_CHARS, height=180)
            label = st.selectbox("Masa berlaku pesan", list(DURATIONS))
            submitted = st.form_submit_button("🔒 Enkripsi & buat pesan", type="primary")

        if submitted:
            if not text.strip():
                st.warning("Pesan tidak boleh kosong.")
            else:
                key = cc.generate_key()
                msg_id = cc.generate_id()
                expires_at = int(time.time()) + DURATIONS[label]
                aad = cc.build_aad(msg_id, expires_at)
                nonce, ciphertext = cc.encrypt(text, key, aad)
                storage.save_message(msg_id, nonce, ciphertext, expires_at)
                st.session_state.created = {
                    "id": msg_id,
                    "key": cc.b64_encode(key),
                    "exp": expires_at,
                }

        created = st.session_state.get("created")
        if created:
            st.success("Pesan terenkripsi dan tersimpan. Kirim ID dan kunci lewat jalur yang BERBEDA.")

            c1, c2 = st.columns(2)
            with c1:
                tema.output_box_header("ID PESAN", "Boleh dikirim via chat biasa / tautan")
                st.code(created["id"], language=None)
            with c2:
                tema.output_box_header("KUNCI RAHASIA", "Kirim via kanal lain; hanya tampil sekarang")
                st.code(created["key"], language=None)

            st.info(
                f"Berlaku sampai {fmt_time(created['exp'])}. Tautan langsung ke halaman baca: "
                f"tambahkan `?id={created['id']}` di akhir alamat aplikasi."
            )

            with st.expander("🔍 Apa yang sebenarnya tersimpan di server?"):
                row = storage.fetch_message(created["id"])
                if row:
                    st.json({
                        "id": row["id"],
                        "nonce (hex)": row["nonce"].hex(),
                        "ciphertext + tag (hex)": row["ciphertext"].hex(),
                        "expires_at": row["expires_at"],
                    })
                    st.caption("Server tidak menyimpan kunci maupun teks asli, hanya data acak di atas.")

            if st.button("🧹 Bersihkan tampilan (hapus kunci dari layar)"):
                st.session_state.pop("created", None)
                st.rerun()

    with col_side:
        security_items = [
            ("🔑", "Kunci 256-bit", "CSPRNG os.urandom", "Dibuat acak di memori server dan tidak pernah disimpan ke disk."),
            ("🛡️", "Nonce 96-bit Unik", "Sekali Pakai", "Setiap enkripsi selalu membuat nonce baru, mencegah replay attack."),
            ("🏷️", "Tag GCM 128-bit", "Integritas & Otentikasi", "Mendeteksi perubahan sekecil 1-bit tanpa memerlukan hashing tambahan."),
            ("⏱️", "AAD Metadata", "ID + Kedaluwarsa", "Metadata diikat langsung ke ciphertext; mengubah waktu membuat dekripsi gagal."),
            ("🔥", "Burn After Reading", "Hapus Seketika", "Pesan langsung dihapus permanen begitu pembaca pertama membukanya."),
        ]
        tema.work_experience_container(security_items, title="Alur & Spesifikasi Kripto")


# ---------------------------------------------------------------- Baca pesan
def page_read():
    col_main, col_side = st.columns([7, 5])

    with col_main:
        tema.page_header("Baca Pesan", "Masukkan ID dan Kunci Rahasia untuk membuka dan memusnahkan pesan.")

        revealed = st.session_state.get("revealed")
        if revealed is not None:
            st.success("Pesan berhasil dibuka dan SUDAH DIHAPUS dari server. Simpan jika perlu.")
            tema.revealed_card_badge()
            st.text_area("Isi pesan", value=revealed, height=180)
            if st.button("Tutup pesan"):
                st.session_state.revealed = None
                st.rerun()
            return

        with st.form("form_baca"):
            msg_id = st.text_input("ID Pesan", value=st.query_params.get("id", ""))
            key_text = st.text_input("Kunci Rahasia", type="password")
            submitted = st.form_submit_button("🔓 Buka pesan (hanya bisa sekali)", type="primary")

        if not submitted:
            pass
        else:
            msg_id = msg_id.strip()
            row = storage.fetch_message(msg_id)
            if row is None:
                st.error("Pesan tidak ditemukan, sudah dibaca, atau sudah kedaluwarsa.")
            else:
                try:
                    key = cc.parse_key(key_text)
                    aad = cc.build_aad(row["id"], row["expires_at"])
                    plaintext = cc.decrypt(row["nonce"], row["ciphertext"], key, aad)
                except cc.DecryptionError as exc:
                    st.error(f"Gagal membuka pesan: {exc}")
                else:
                    # Hapus dulu secara atomik; hanya satu pembaca yang boleh melihat isi pesan.
                    if storage.consume_message(msg_id):
                        st.session_state.revealed = plaintext
                        st.rerun()
                    else:
                        st.error("Pesan ini baru saja dibuka oleh pihak lain.")

    with col_side:
        reader_guide = [
            ("📩", "ID Pesan", "Kunci Pencarian", "ID digunakan untuk melacak baris ciphertext unik yang tersimpan di server."),
            ("🔑", "Kunci Rahasia", "AES-256 Key", "Kunci 256-bit base64 hanya diketahui penerima dan tidak pernah dicatat server."),
            ("⚠️", "Hanya Sekali Baca", "Musnah Otomatis", "Ciphertext langsung dihapus permanen. Refresh halaman akan menghilangkan pesan."),
        ]
        tema.work_experience_container(reader_guide, title="Panduan Penerima")


# ----------------------------------------------------------- Bukti keamanan
def page_proof():
    tema.page_header("Bukti Keamanan", "Verifikasi integritas kriptografi AES-256-GCM secara mandiri.")
    st.write(
        "Halaman ini menjalankan pengujian langsung untuk menunjukkan bahwa **satu algoritma, "
        "AES-256-GCM, sudah mencukupi**: menjaga kerahasiaan, mendeteksi data yang diubah, "
        "dan melindungi metadata, tanpa hash atau cipher tambahan."
    )

    if st.button("▶️ Jalankan semua pengujian", type="primary"):
        st.session_state.test_results = selftest.run_all()

    if "test_results" not in st.session_state:
        st.session_state.test_results = selftest.run_all()

    results = st.session_state.test_results
    passed = sum(r["Hasil"] == "LULUS" for r in results)

    tema.security_proof_overview(len(results), passed)

    st.markdown('<div class="en-work-title" style="margin-top: 1.5rem; margin-bottom: 0.75rem;">Rincian 9 Pengujian Integritas Kripto</div>', unsafe_allow_html=True)

    cols = st.columns(3)
    for idx, r in enumerate(results):
        with cols[idx % 3]:
            tema.test_card(r["Pengujian"], r["Hasil"] == "LULUS", r["Keterangan"])


# ------------------------------------------------------------------- Tentang
def page_about():
    col_main, col_side = st.columns([7, 5])

    with col_main:
        tema.page_header("Tentang EmberNote", "Pesan rahasia sekali baca (burn-after-reading).")
        st.markdown(
            """
<div class="en-card en-card-cream">
    <h3 style="font-family: 'Space Grotesk', sans-serif; margin-top: 0; font-size: 1.3rem;">EmberNote: Burn-After-Reading</h3>
    <p style="font-family: 'Space Mono', monospace; font-size: 0.88rem; line-height: 1.5; color: #222;">
        Aplikasi pesan rahasia sekali baca yang dirancang dengan prinsip minimalis kriptografi: 
        <strong>satu algoritma AES-256-GCM</strong> sudah mencukupi untuk menjamin kerahasiaan, integritas data, dan otentikasi metadata.
    </p>
    <hr style="border: 1px solid #111; opacity: 0.15; margin: 16px 0;">
    <h4 style="font-family: 'Space Grotesk', sans-serif; margin-bottom: 8px; font-size: 1.05rem;">Algoritma Tunggal: AES-256-GCM</h4>
    <ul style="font-family: 'Space Mono', monospace; font-size: 0.82rem; line-height: 1.6; padding-left: 20px; color: #222;">
        <li><strong>Kunci 256-bit:</strong> Dibuat acak oleh CSPRNG sistem operasi (<code>os.urandom</code>), tidak diturunkan dari password.</li>
        <li><strong>Nonce 96-bit:</strong> Dibuat unik untuk setiap kali operasi enkripsi dijalankan, mencegah replay attack.</li>
        <li><strong>AAD (Additional Authenticated Data):</strong> Mengikat ID pesan dan waktu kedaluwarsa langsung ke tag otentikasi. Mengubah metadata membuat dekripsi otomatis gagal.</li>
        <li><strong>Server Minim Informasi:</strong> Server hanya menyimpan ciphertext + tag dan nonce. Kunci rahasia tidak pernah disimpan atau dicatat di server.</li>
    </ul>
    <hr style="border: 1px solid #111; opacity: 0.15; margin: 16px 0;">
    <h4 style="font-family: 'Space Grotesk', sans-serif; margin-bottom: 8px; font-size: 1.05rem;">Alur Kerja Sistem</h4>
    <ol style="font-family: 'Space Mono', monospace; font-size: 0.82rem; line-height: 1.6; padding-left: 20px; color: #222;">
        <li><strong>Enkripsi:</strong> Pengirim menulis pesan, aplikasi membuat kunci acak 256-bit di memori, mengenkripsi pesan, dan menyimpan ciphertext ke server.</li>
        <li><strong>Distribusi:</strong> Pengirim membagikan <em>ID Pesan</em> dan <em>Kunci Rahasia</em> melalui dua saluran komunikasi yang berbeda.</li>
        <li><strong>Dekripsi & Pemusnahan:</strong> Penerima memasukkan ID dan Kunci, server memverifikasi otentikasi AES-GCM, menghapus data secara atomik, dan menampilkan pesan asli.</li>
    </ol>
    <p style="font-family: 'Space Mono', monospace; font-size: 0.78rem; color: #666; margin-top: 14px; margin-bottom: 0;">
        <em>*Proyek pembelajaran kriptografi, bukan alat keamanan untuk produksi.</em>
    </p>
</div>
            """,
            unsafe_allow_html=True,
        )

    with col_side:
        threat_items = [
            ("💻", "Bukan E2EE Murni", "Pemrosesan Server", "Kunci dibuat dan dipakai di memori server saat pesan dibuat atau dibuka."),
            ("🔀", "Wajib Dua Jalur Berbeda", "Keamanan Pengiriman", "Siapa pun yang memegang ID + kunci dapat membuka pesan; pisahkan jalur chat."),
            ("📏", "Panjang & Waktu Terbuka", "Metadata Tidak Tersembunyi", "Panjang ciphertext, ID unik, dan waktu kedaluwarsa tidak disamarkan."),
            ("🛡️", "Tanpa Rate Limiting", "Perlindungan Brute-force", "Tidak ada CAPTCHA, namun menebak ruang kunci 2^256 secara komputasi mustahil."),
            ("☁️", "Penyimpanan Sementara", "Streamlit Ephemeral", "Database SQLite bersifat sementara dan terhapus bila server reboot."),
            ("👁️", "Plaintext di Sesi Browser", "Peramban Penerima", "Plaintext tetap ada di tampilan layar sampai tombol tutup ditekan."),
            ("🔍", "Belum Diaudit", "Proyek Edukatif", "Dibuat untuk tujuan eksplorasi kriptografi, belum diaudit pihak independen."),
        ]
        tema.work_experience_container(threat_items, title="⚠️ Batasan & Ancaman")


if "page" not in st.session_state:
    st.session_state.page = PAGES[1] if "id" in st.query_params else PAGES[0]

tema.sidebar_brand()
choice = st.sidebar.radio("Menu", PAGES, key="page")
tema.sidebar_footer()

{PAGES[0]: page_create, PAGES[1]: page_read, PAGES[2]: page_proof, PAGES[3]: page_about}[choice]()
