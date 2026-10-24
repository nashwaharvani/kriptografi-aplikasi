"""EmberNote - Pesan rahasia sekali baca berbasis AES-256-GCM (Streamlit)."""
import time
from datetime import datetime, timedelta, timezone

from pathlib import Path

import streamlit as st

import tema
from modules import aes_gcm as cc
from modules import selftest, storage

st.set_page_config(page_title="EmberNote", page_icon="🔥", layout="centered")
tema.apply_theme()

LOGO = Path(__file__).parent / "images" / "logo.png"

MAX_CHARS = 5000
DURATIONS = {"5 menit": 300, "1 jam": 3600, "24 jam": 86400, "7 hari": 604800}
PAGES = ["🔥 Buat Pesan", "📖 Baca Pesan", "🛡️ Bukti Keamanan", "ℹ️ Tentang"]
WIB = timezone(timedelta(hours=7))


def fmt_time(ts: int) -> str:
    return datetime.fromtimestamp(ts, WIB).strftime("%d %b %Y %H:%M:%S WIB")


# ---------------------------------------------------------------- Buat pesan
def page_create():
    st.header("🔥 Buat Pesan Rahasia Sekali Baca")
    st.caption("Pesan dienkripsi dengan AES-256-GCM, dibuka sekali, lalu hangus.")

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
                "id": msg_id, "key": cc.b64_encode(key), "exp": expires_at,
            }

    created = st.session_state.get("created")
    if not created:
        return

    st.success("Pesan terenkripsi dan tersimpan. Kirim ID dan kunci lewat jalur yang BERBEDA.")
    st.markdown("**ID Pesan** (boleh dikirim lewat chat biasa)")
    st.code(created["id"], language=None)
    st.markdown("**Kunci Rahasia** (kirim lewat jalur lain; hanya ditampilkan sekarang)")
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


# ---------------------------------------------------------------- Baca pesan
def page_read():
    st.header("📖 Baca Pesan Rahasia")

    revealed = st.session_state.get("revealed")
    if revealed is not None:
        st.success("Pesan berhasil dibuka dan SUDAH DIHAPUS dari server. Simpan jika perlu.")
        st.text_area("Isi pesan", value=revealed, height=200)
        if st.button("Tutup pesan"):
            st.session_state.revealed = None
            st.rerun()
        return

    with st.form("form_baca"):
        msg_id = st.text_input("ID Pesan", value=st.query_params.get("id", ""))
        key_text = st.text_input("Kunci Rahasia", type="password")
        submitted = st.form_submit_button("🔓 Buka pesan (hanya bisa sekali)", type="primary")

    if not submitted:
        return

    msg_id = msg_id.strip()
    row = storage.fetch_message(msg_id)
    if row is None:
        st.error("Pesan tidak ditemukan, sudah dibaca, atau sudah kedaluwarsa.")
        return
    try:
        key = cc.parse_key(key_text)
        aad = cc.build_aad(row["id"], row["expires_at"])
        plaintext = cc.decrypt(row["nonce"], row["ciphertext"], key, aad)
    except cc.DecryptionError as exc:
        st.error(f"Gagal membuka pesan: {exc}")
        return

    # Hapus dulu secara atomik; hanya satu pembaca yang boleh melihat isi pesan.
    if storage.consume_message(msg_id):
        st.session_state.revealed = plaintext
        st.rerun()
    else:
        st.error("Pesan ini baru saja dibuka oleh pihak lain.")


# ----------------------------------------------------------- Bukti keamanan
def page_proof():
    st.header("🛡️ Bukti Keamanan")
    st.write(
        "Halaman ini menjalankan pengujian langsung untuk menunjukkan bahwa **satu algoritma, "
        "AES-256-GCM, sudah mencukupi**: menjaga kerahasiaan, mendeteksi data yang diubah, "
        "dan melindungi metadata, tanpa hash atau cipher tambahan."
    )
    if st.button("▶️ Jalankan semua pengujian", type="primary"):
        results = selftest.run_all()
        passed = sum(r["Hasil"] == "LULUS" for r in results)
        (st.success if passed == len(results) else st.error)(
            f"{passed} dari {len(results)} pengujian lulus."
        )
        st.table(results)


# ------------------------------------------------------------------- Tentang
def page_about():
    st.header("ℹ️ Tentang EmberNote")
    st.markdown(
        """
**EmberNote** adalah aplikasi pesan rahasia sekali baca (*burn-after-reading*).

**Algoritma tunggal: AES-256-GCM**
- Kunci 256-bit dibuat acak oleh CSPRNG sistem operasi (`os.urandom`), tidak diturunkan dari password.
- Nonce 96-bit baru dibuat untuk setiap enkripsi.
- **AAD** mengikat `ID pesan` dan `waktu kedaluwarsa` ke ciphertext, sehingga mengubah metadata membuat dekripsi gagal.
- Server hanya menyimpan nonce dan ciphertext+tag. Kunci tidak pernah disimpan.

**Alur**
1. Pengirim menulis pesan, aplikasi membuat kunci acak, mengenkripsi, dan menyimpan ciphertext.
2. Pengirim membagikan *ID* dan *kunci* lewat dua jalur berbeda.
3. Penerima memasukkan keduanya, pesan didekripsi dan diverifikasi, lalu dihapus dari server.

*Proyek pembelajaran kriptografi, bukan alat keamanan untuk produksi.*
        """
    )
    with st.expander("⚠️ Batasan & ancaman yang tidak ditangani"):
        st.markdown(
            """
- **Bukan E2EE murni**: kunci dibuat dan dipakai di server saat pesan dibuat/dibuka.
- Siapa pun yang memegang **ID + kunci** dapat membuka pesan, jadi kirim keduanya lewat jalur berbeda.
- **Panjang pesan, ID, dan waktu** tidak tersembunyi.
- Tidak ada pembatasan spam/percobaan (menebak kunci 256-bit tetap mustahil).
- Penyimpanan Streamlit Cloud bersifat sementara.
- Plaintext tetap ada di sesi browser sampai pesan ditutup.
- Belum diaudit pihak independen.
            """
        )


if "page" not in st.session_state:
    st.session_state.page = PAGES[1] if "id" in st.query_params else PAGES[0]

if LOGO.exists():
    st.sidebar.image(str(LOGO), width=96)
st.sidebar.title("EmberNote")
choice = st.sidebar.radio("Menu", PAGES, key="page")
st.sidebar.caption("AES-256-GCM • Pesan sekali baca")

tema.hero("EmberNote", "Pesan rahasia sekali baca, dilindungi satu algoritma.",
          ("AES-256-GCM", "Sekali baca", "AAD"))
{PAGES[0]: page_create, PAGES[1]: page_read, PAGES[2]: page_proof, PAGES[3]: page_about}[choice]()
