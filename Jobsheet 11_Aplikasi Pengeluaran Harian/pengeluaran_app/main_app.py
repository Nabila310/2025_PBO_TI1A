# main_app.py

import streamlit as st
import datetime
import pandas as pd
import locale

# --- Setting Locale ---
try:
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Indonesian_Indonesia.1252')
    except:
        print("Locale id_ID/Indonesian tidak tersedia.")

def format_rp(angka):
    """Format angka ke Rupiah."""
    try:
        return locale.currency(angka or 0, grouping=True, symbol='Rp ')[:-3]
    except:
        return f"Rp {angka or 0:,.0f}".replace(",", ".")


# --- Import Modul Internal ---
try:
    from model import Transaksi
    from manager_anggaran import AnggaranHarian # PERBAIKI: Ganti 'manajer_anggaran' menjadi 'manager_anggaran'
    from konfigurasi import KATEGORI_PENGELUARAN
except ImportError as e:
    st.error(f"Gagal mengimpor modul: {e}. Pastikan file .py lain ada.")
    st.stop()


# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Catatan Pengeluaran", layout="wide", initial_sidebar_state="expanded")


# --- Inisialisasi Pengelola Anggaran (gunakan cache) ---
@st.cache_resource
def get_anggaran_manager():
    print(">>> STREAMLIT: (Cache Resource) Menginisialisasi AnggaranHarian...")
    return AnggaranHarian()

anggaran = get_anggaran_manager()


# --- Halaman Tambah Transaksi ---
def halaman_input(anggaran: AnggaranHarian):
    st.header("Tambah Pengeluaran Baru")
    with st.form("form_transaksi_baru", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            deskripsi = st.text_input("Deskripsi*", placeholder="Contoh: Makan siang")
        with col2:
            kategori = st.selectbox("Kategori*:", KATEGORI_PENGELUARAN, index=0)

        col3, col4 = st.columns(2)
        with col3:
            jumlah = st.number_input("Jumlah (Rp)*:", min_value=0.01, step=1000.0, format="%.0f", value=None, placeholder="Contoh: 25000")
        with col4:
            tanggal = st.date_input("Tanggal*:", value=datetime.date.today())

        submitted = st.form_submit_button("Simpan Transaksi")
        if submitted:
            if not deskripsi:
                st.warning("Deskripsi wajib!")
            elif jumlah is None or jumlah <= 0:
                st.warning("Jumlah wajib!")
            else:
                with st.spinner("Menyimpan..."):
                    tx = Transaksi(deskripsi, float(jumlah), kategori, tanggal)
                    if anggaran.tambah_transaksi(tx):
                        st.success("OK! Disimpan.")
                        st.cache_data.clear() # Hapus cache agar data terbaru dimuat
                        st.rerun() # Refresh aplikasi
                    else:
                        st.error("Gagal menyimpan.")


# --- Halaman Riwayat ---
def halaman_riwayat(anggaran: AnggaranHarian):
    st.subheader("Detail Semua Transaksi")
    if st.button("Refresh Riwayat"):
        st.cache_data.clear() # Hapus cache agar data terbaru dimuat
        st.rerun() # Refresh aplikasi

    with st.spinner("Memuat riwayat..."):
        df_transaksi = anggaran.get_dataframe_transaksi()

    if df_transaksi is None:
        st.error("Gagal mengambil riwayat.")
    elif df_transaksi.empty:
        st.info("Belum ada transaksi.")
    else:
        st.dataframe(df_transaksi, use_container_width=True, hide_index=True)

        # --- Fungsionalitas Hapus Transaksi ---
        st.markdown("---")
        st.subheader("Hapus Transaksi")
        st.warning("Perhatian: Penghapusan transaksi bersifat permanen.")

        col_del1, col_del2 = st.columns([1, 2])
        with col_del1:
            id_to_delete = st.number_input(
                "Masukkan ID Transaksi yang ingin dihapus:",
                min_value=1,
                step=1,
                value=None,
                placeholder="Contoh: 101",
                key="id_delete_input"
            )
        with col_del2:
            st.markdown("<br>", unsafe_allow_html=True) # Spacer
            if st.button("Hapus Transaksi Terpilih", key="delete_button"):
                if id_to_delete is None:
                    st.error("Mohon masukkan ID transaksi yang valid.")
                else:
                    # Konfirmasi Penghapusan
                    st.session_state['confirm_delete_id'] = id_to_delete
                    st.session_state['show_confirm_dialog'] = True

        if st.session_state.get('show_confirm_dialog', False):
            with st.expander(f"Konfirmasi Penghapusan ID: {st.session_state['confirm_delete_id']}", expanded=True):
                st.warning(f"Anda yakin ingin menghapus transaksi dengan ID **{st.session_state['confirm_delete_id']}**? Tindakan ini tidak dapat dibatalkan.")
                col_confirm_btn1, col_confirm_btn2 = st.columns(2)
                with col_confirm_btn1:
                    if st.button("YA, Hapus Sekarang!", key="confirm_delete_yes"):
                        with st.spinner("Menghapus..."):
                            if anggaran.hapus_transaksi(st.session_state['confirm_delete_id']):
                                st.success(f"Transaksi dengan ID {st.session_state['confirm_delete_id']} berhasil dihapus!")
                                st.cache_data.clear() # Bersihkan cache
                                st.session_state['show_confirm_dialog'] = False # Sembunyikan dialog
                                st.rerun() # Refresh tampilan
                            else:
                                st.error(f"Gagal menghapus transaksi dengan ID {st.session_state['confirm_delete_id']}. Pastikan ID benar.")
                                st.session_state['show_confirm_dialog'] = False # Sembunyikan dialog
                                st.rerun() # Refresh tampilan (opsional)
                with col_confirm_btn2:
                    if st.button("TIDAK, Batalkan", key="confirm_delete_no"):
                        st.info("Penghapusan dibatalkan.")
                        st.session_state['show_confirm_dialog'] = False # Sembunyikan dialog
                        st.rerun() # Refresh tampilan (opsional)


# --- Halaman Ringkasan ---
def halaman_ringkasan(anggaran: AnggaranHarian):
    st.subheader("Ringkasan Pengeluaran")
    col_filter1, col_filter2 = st.columns([1, 2])

    with col_filter1:
        pilihan_periode = st.selectbox("Filter Periode:", ["Semua Waktu", "Hari Ini", "Pilih Tanggal"], key="filter_periode", on_change=lambda: st.cache_data.clear())

    tanggal_filter = None
    label_periode = "(Semua Waktu)"

    if pilihan_periode == "Hari Ini":
        tanggal_filter = datetime.date.today()
        label_periode = f"({tanggal_filter.strftime('%d %b')})"
    elif pilihan_periode == "Pilih Tanggal":
        if 'tanggal_pilihan_state' not in st.session_state:
            st.session_state.tanggal_pilihan_state = datetime.date.today()
        tanggal_filter = st.date_input("Pilih Tanggal:", value=st.session_state.tanggal_pilihan_state, key="tanggal_pilihan", on_change=lambda: setattr(st.session_state, 'tanggal_pilihan_state', st.session_state.tanggal_pilihan) or st.cache_data.clear())
        label_periode = f"({tanggal_filter.strftime('%d %b %Y')})"

    with col_filter2:
        @st.cache_data(ttl=300)
        def hitung_total_cached(tgl_filter):
            return anggaran.hitung_total_pengeluaran(tanggal=tgl_filter)

        total_pengeluaran = hitung_total_cached(tanggal_filter)
        st.metric(label=f"Total Pengeluaran {label_periode}", value=format_rp(total_pengeluaran))

    st.divider()
    st.subheader(f"Pengeluaran per Kategori {label_periode}")

    @st.cache_data(ttl=300)
    def get_kategori_cached(tgl_filter):
        return anggaran.get_pengeluaran_per_kategori(tanggal=tgl_filter)

    with st.spinner(f"Memuat ringkasan kategori..."):
        dict_per_kategori = get_kategori_cached(tanggal_filter)

    if not dict_per_kategori:
        st.info(f"Tidak ada data untuk periode ini.")
    else:
        try:
            data_kategori = [{"Kategori": kat, "Total": jml} for kat, jml in dict_per_kategori.items()]
            df_kategori = pd.DataFrame(data_kategori).sort_values(by="Total", ascending=False).reset_index(drop=True)
            df_kategori['Total (Rp)'] = df_kategori['Total'].apply(format_rp)

            col_kat1, col_kat2 = st.columns(2)
            with col_kat1:
                st.write("Tabel:")
                st.dataframe(df_kategori[['Kategori', 'Total (Rp)']], hide_index=True, use_container_width=True)

            with col_kat2:
                st.write("Grafik:")
                st.bar_chart(df_kategori.set_index('Kategori')['Total'], use_container_width=True)
        except Exception as e:
            st.error(f"Gagal tampilkan ringkasan: {e}")


# --- Fungsi Utama Aplikasi Streamlit ---
def main():
    st.sidebar.title("Catatan Pengeluaran")
    menu_pilihan = st.sidebar.radio("Pilih Menu:", ["Tambah", "Riwayat", "Ringkasan"], key="menu_utama")
    st.sidebar.markdown("---")
    st.sidebar.info("Jobsheet - Aplikasi Keuangan")

    manajer_anggaran = get_anggaran_manager()

    if menu_pilihan == "Tambah":
        halaman_input(manajer_anggaran)
    elif menu_pilihan == "Riwayat":
        halaman_riwayat(manajer_anggaran)
    elif menu_pilihan == "Ringkasan":
        halaman_ringkasan(manajer_anggaran)

    st.markdown("---")
    st.caption("Pengembangan Aplikasi Berbasis OOP")


if __name__ == "__main__":
    main()