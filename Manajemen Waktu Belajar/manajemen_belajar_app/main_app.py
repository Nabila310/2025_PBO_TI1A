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

def format_durasi(menit_total):
    """Format total menit menjadi HH jam MM menit."""
    if menit_total is None or menit_total == 0:
        return "0 menit"
    jam = int(menit_total // 60)
    sisa_menit = int(menit_total % 60)
    
    parts = []
    if jam > 0:
        parts.append(f"{jam} jam")
    if sisa_menit > 0:
        parts.append(f"{sisa_menit} menit")
    
    return " ".join(parts) if parts else "0 menit"


# --- Import Modul Internal ---
try:
    from model import SesiBelajar
    from manager_belajar import ManajerBelajar
    from konfigurasi import MATAKULIAH_PILIHAN, TINGKAT_PEMAHAMAN_PILIHAN
except ImportError as e:
    st.error(f"Gagal mengimpor modul: {e}. Pastikan file .py lain ada di direktori yang benar.")
    st.stop()


# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Aplikasi Manajemen Belajar", layout="wide", initial_sidebar_state="expanded")


# --- Inisialisasi Manajer Belajar (gunakan cache) ---
@st.cache_resource
def get_manajer_belajar():
    print(">>> STREAMLIT: (Cache Resource) Menginisialisasi ManajerBelajar...")
    return ManajerBelajar()

manajer = get_manajer_belajar()


# --- Halaman Tambah Sesi Belajar ---
def halaman_input(manajer: ManajerBelajar):
    st.header("📚 Tambah Sesi Belajar Baru")
    with st.form("form_sesi_belajar_baru", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            mata_kuliah = st.selectbox("Mata Kuliah*:", MATAKULIAH_PILIHAN, index=len(MATAKULIAH_PILIHAN)-1)
            topik = st.text_input("Topik*", placeholder="Contoh: OOP dan Database")
        with col2:
            durasi_menit = st.number_input("Durasi (Menit)*:", min_value=0.01, step=5.0, format="%.0f", value=None, placeholder="Contoh: 90")
            tanggal = st.date_input("Tanggal*:", value=datetime.date.today())

            tingkat_pemahaman = st.selectbox("Tingkat Pemahaman:", TINGKAT_PEMAHAMAN_PILIHAN, index=1)

        submitted = st.form_submit_button("✅ Simpan Sesi Belajar")
        if submitted:
            if not mata_kuliah or mata_kuliah == "Pilih Kategori":
                st.warning("Mata Kuliah wajib diisi!", icon="⚠️")
            elif not topik:
                st.warning("Topik wajib diisi!", icon="⚠️")
            elif durasi_menit is None or durasi_menit <= 0:
                st.warning("Durasi wajib dan harus lebih dari 0!", icon="⚠️")
            else:
                with st.spinner("Menyimpan..."):
                    sesi = SesiBelajar(mata_kuliah, topik, float(durasi_menit), tanggal, tingkat_pemahaman)
                    if manajer.tambah_sesi_belajar(sesi):
                        st.success(f"OK! Sesi belajar berhasil disimpan.", icon="✅")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Gagal menyimpan sesi belajar.", icon="❌")


# --- Halaman Riwayat ---
def halaman_riwayat(manajer: ManajerBelajar):
    st.subheader("📖 Detail Semua Sesi Belajar")
    if st.button("🔄 Refresh Riwayat"):
        st.cache_data.clear()
        st.rerun()

    with st.spinner("Memuat riwayat..."):
        df_sesi = manajer.get_dataframe_sesi_belajar(None)

    if df_sesi is None:
        st.error("Gagal mengambil riwayat.")
    elif df_sesi.empty:
        st.info("Belum ada sesi belajar.")
    else:
        st.dataframe(df_sesi, use_container_width=True, hide_index=True)

        # --- Fungsionalitas Hapus Sesi Belajar (sesuai Jobsheet 11) ---
        st.markdown("---")
        st.subheader("🗑️ Hapus Sesi Belajar")
        st.warning("Perhatian: Penghapusan sesi belajar bersifat permanen.")

        col_del1, col_del2 = st.columns([1, 2])
        with col_del1:
            id_to_delete = st.number_input(
                "Masukkan ID Sesi yang ingin dihapus:",
                min_value=1,
                step=1,
                value=None,
                placeholder="Contoh: 101",
                key="id_delete_input"
            )
        with col_del2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Hapus Sesi Terpilih", key="delete_button"):
                if id_to_delete is None:
                    st.error("Mohon masukkan ID sesi belajar yang valid.")
                else:
                    st.session_state['confirm_delete_id'] = id_to_delete
                    st.session_state['show_confirm_dialog'] = True

        if st.session_state.get('show_confirm_dialog', False):
            dialog_placeholder = st.empty()
            with dialog_placeholder.expander(f"Konfirmasi Penghapusan ID: {st.session_state['confirm_delete_id']}", expanded=True):
                st.warning(f"Anda yakin ingin menghapus sesi belajar dengan ID **{st.session_state['confirm_delete_id']}**? Tindakan ini tidak dapat dibatalkan.")
                col_confirm_btn1, col_confirm_btn2 = st.columns(2)
                with col_confirm_btn1:
                    if st.button("YA, Hapus Sekarang!", key="confirm_delete_yes"):
                        with st.spinner("Menghapus..."):
                            if manajer.hapus_sesi_belajar(st.session_state['confirm_delete_id']):
                                st.success(f"Sesi dengan ID {st.session_state['confirm_delete_id']} berhasil dihapus!")
                                st.cache_data.clear()
                                st.session_state['show_confirm_dialog'] = False
                                dialog_placeholder.empty()
                                st.rerun()
                            else:
                                st.error(f"Gagal menghapus sesi dengan ID {st.session_state['confirm_delete_id']}. Pastikan ID benar atau terjadi kesalahan DB.")
                                st.session_state['show_confirm_dialog'] = False
                                dialog_placeholder.empty()
                with col_confirm_btn2:
                    if st.button("TIDAK, Batalkan", key="confirm_delete_no"):
                        st.info("Penghapusan dibatalkan.")
                        st.session_state['show_confirm_dialog'] = False
                        dialog_placeholder.empty()
        

# --- Halaman Ringkasan ---
def halaman_ringkasan(manajer: ManajerBelajar):
    st.subheader("📊 Ringkasan Sesi Belajar")
    col_filter1, col_filter2 = st.columns([1, 2])

    with col_filter1:
        pilihan_periode = st.selectbox("Filter Periode:", ["Semua Waktu", "Hari Ini", "Pilih Tanggal"], key="filter_periode_ringkasan", on_change=lambda: st.cache_data.clear())

    tanggal_filter = None; label_periode = "(Semua Waktu)"

    if pilihan_periode == "Hari Ini":
        tanggal_filter = datetime.date.today(); label_periode = f"({tanggal_filter.strftime('%d %b %Y')})"
    elif pilihan_periode == "Pilih Tanggal":
        if 'tanggal_pilihan_state_ringkasan' not in st.session_state:
            st.session_state.tanggal_pilihan_state_ringkasan = datetime.date.today()
        tanggal_filter = st.date_input("Pilih Tanggal:", value=st.session_state.tanggal_pilihan_state_ringkasan, key="tanggal_pilihan_ringkasan", on_change=lambda: setattr(st.session_state, 'tanggal_pilihan_state_ringkasan', st.session_state.tanggal_pilihan_ringkasan) or st.cache_data.clear())
        label_periode = f"({tanggal_filter.strftime('%d %b %Y')})"

    with col_filter2:
        @st.cache_data(ttl=300)
        def hitung_total_cached(tgl_filter):
            return manajer.hitung_total_durasi_belajar(tanggal=tgl_filter)

        total_durasi_belajar = hitung_total_cached(tanggal_filter)
        st.metric(label=f"Total Durasi Belajar {label_periode}", value=format_durasi(total_durasi_belajar))

    st.divider()
    st.subheader(f"Durasi Belajar per Mata Kuliah {label_periode}")

    @st.cache_data(ttl=300)
    def get_matkul_cached(tgl_filter):
        return manajer.get_durasi_per_mata_kuliah(tanggal=tgl_filter)

    with st.spinner(f"Memuat ringkasan mata kuliah..."):
        dict_per_matkul = get_matkul_cached(tanggal_filter)

    if not dict_per_matkul:
        st.info(f"Tidak ada data untuk periode ini.")
    else:
        try:
            data_matkul = [{"Mata Kuliah": kat, "Total Durasi (Menit)": jml} for kat, jml in dict_per_matkul.items()]
            df_matkul = pd.DataFrame(data_matkul).sort_values(by="Total Durasi (Menit)", ascending=False).reset_index(drop=True)
            df_matkul['Total Durasi'] = df_matkul['Total Durasi (Menit)'].apply(format_durasi)

            col_matkul1, col_matkul2 = st.columns(2)
            with col_matkul1:
                st.write("Tabel:")
                st.dataframe(df_matkul[['Mata Kuliah', 'Total Durasi']], hide_index=True, use_container_width=True)

            with col_matkul2:
                st.write("Grafik:")
                st.bar_chart(df_matkul.set_index('Mata Kuliah')['Total Durasi (Menit)'], use_container_width=True)
        except Exception as e:
            st.error(f"Gagal tampilkan ringkasan mata kuliah: {e}")

    st.divider()
    st.subheader(f"Distribusi Tingkat Pemahaman per Topik {label_periode}")

    @st.cache_data(ttl=300)
    def get_pemahaman_distribusi_cached(tgl_filter):
        return manajer.get_distribusi_pemahaman_per_topik(tanggal=tgl_filter)

    with st.spinner(f"Memuat distribusi pemahaman..."):
        dict_distribusi_pemahaman = get_pemahaman_distribusi_cached(tanggal_filter)

    if not dict_distribusi_pemahaman:
        st.info(f"Tidak ada data distribusi pemahaman untuk periode ini.")
    else:
        try:
            data_distribusi = []
            for topik, distribusi in dict_distribusi_pemahaman.items():
                row = {"Topik": topik}
                for level in TINGKAT_PEMAHAMAN_PILIHAN:
                    row[level] = distribusi.get(level, 0)
                data_distribusi.append(row)
            df_distribusi = pd.DataFrame(data_distribusi)

            if not df_distribusi.empty:
                st.write("Jumlah Sesi berdasarkan Tingkat Pemahaman per Topik:")
                st.dataframe(df_distribusi, hide_index=True, use_container_width=True)

                st.write("Grafik Distribusi Tingkat Pemahaman (Top 5 Topik dengan Sesi Terbanyak):")
                
                df_distribusi['Total Sesi'] = df_distribusi[TINGKAT_PEMAHAMAN_PILIHAN].sum(axis=1)
                df_plot = df_distribusi.sort_values(by='Total Sesi', ascending=False).head(5)
                
                if not df_plot.empty:
                    df_melted = df_plot.melt(id_vars=['Topik'], value_vars=TINGKAT_PEMAHAMAN_PILIHAN,
                                             var_name='Tingkat Pemahaman', value_name='Jumlah Sesi')
                    
                    chart = st.bar_chart(
                        df_melted,
                        x='Topik',
                        y='Jumlah Sesi',
                        color='Tingkat Pemahaman',
                        use_container_width=True
                    )
                else:
                    st.info("Tidak cukup data untuk menampilkan grafik distribusi pemahaman.")

        except Exception as e:
            st.error(f"Gagal tampilkan distribusi pemahaman: {e}")


# --- Fungsi Utama Aplikasi Streamlit ---
def main():
    st.sidebar.title("🧠 Aplikasi Manajemen Belajar")
    menu_pilihan = st.sidebar.radio("Pilih Menu:", ["Tambah Sesi", "Riwayat", "Ringkasan"], key="menu_utama")
    st.sidebar.markdown("---")
    st.sidebar.info("Jobsheet - Integrasi OOP dalam Aplikasi Sederhana")

    if menu_pilihan == "Tambah Sesi":
        halaman_input(manajer)
    elif menu_pilihan == "Riwayat":
        halaman_riwayat(manajer)
    elif menu_pilihan == "Ringkasan":
        halaman_ringkasan(manajer)

    st.markdown("---")
    st.caption("Pengembangan Aplikasi Berbasis OOP")


if __name__ == "__main__":
    main()