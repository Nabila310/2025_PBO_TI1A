# manager_anggaran.py

import datetime
import pandas as pd
from model import Transaksi
import database  # Impor modul database kita


class AnggaranHarian:
    """Mengelola logika bisnis pengeluaran harian (Repository Pattern)."""

    _db_setup_done = False  # Flag untuk memastikan setup DB hanya dicek sekali per sesi

    def __init__(self):
        if not AnggaranHarian._db_setup_done:
            print("[AnggaranHarian] Melakukan pengecekan/setup database awal...")
            if database.setup_database_initial():  # Panggil fungsi setup dari database.py
                AnggaranHarian._db_setup_done = True
                print("[AnggaranHarian] Database siap.")
            else:
                print("[AnggaranHarian] KRITIKAL: Setup database awal GAGAL!")

    def tambah_transaksi(self, transaksi: Transaksi) -> bool:
        """Menambahkan transaksi baru ke database."""
        if not isinstance(transaksi, Transaksi) or transaksi.jumlah <= 0:
            return False

        sql = "INSERT INTO transaksi (deskripsi, jumlah, kategori, tanggal) VALUES (?, ?, ?, ?)"
        params = (
            transaksi.deskripsi,
            transaksi.jumlah,
            transaksi.kategori,
            transaksi.tanggal.strftime("%Y-%m-%d")
        )

        return database.execute_query(sql, params) # execute_query sekarang mengembalikan bool

    def get_semua_transaksi_obj(self) -> list[Transaksi]:
        """Mengambil semua transaksi dari database dalam bentuk list Transaksi."""
        sql = "SELECT id, deskripsi, jumlah, kategori, tanggal FROM transaksi ORDER BY tanggal DESC, id DESC"
        rows = database.fetch_query(sql, fetch_all=True)

        transaksi_list = []
        if rows:
            for row in rows:
                transaksi = Transaksi(
                    id_transaksi=row['id'],
                    deskripsi=row['deskripsi'],
                    jumlah=row['jumlah'],
                    kategori=row['kategori'],
                    tanggal=row['tanggal']
                )
                transaksi_list.append(transaksi)
        return transaksi_list

    def get_dataframe_transaksi(self, filter_tanggal: datetime.date | None = None) -> pd.DataFrame:
        """Mengambil transaksi dalam bentuk DataFrame Pandas, bisa difilter berdasarkan tanggal."""
        query = "SELECT id, tanggal, kategori, deskripsi, jumlah FROM transaksi" # Tambahkan 'id' di sini
        params = None

        if filter_tanggal:
            query += " WHERE tanggal = ?"
            params = (filter_tanggal.strftime("%Y-%m-%d"),)

        query += " ORDER BY tanggal DESC, id DESC"
        df = database.get_dataframe(query, params=params)

        if not df.empty:
            try:
                import locale
                locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
                df['Jumlah (Rp)'] = df['jumlah'].map(lambda x: locale.currency(x or 0, grouping=True, symbol='Rp ')[:-3])
            except Exception:
                df['Jumlah (Rp)'] = df['jumlah'].map(lambda x: f"Rp {x or 0:,.0f}".replace(",", "."))

            # Pastikan 'ID' ada di DataFrame untuk ditampilkan di frontend
            df = df[['id', 'tanggal', 'kategori', 'deskripsi', 'Jumlah (Rp)']]
        return df

    def hitung_total_pengeluaran(self, tanggal: datetime.date | None = None) -> float:
        """Menghitung total pengeluaran pada tanggal tertentu (atau seluruhnya jika tidak diberi tanggal)."""
        sql = "SELECT SUM(jumlah) FROM transaksi"
        params = None

        if tanggal:
            sql += " WHERE tanggal = ?"
            params = (tanggal.strftime("%Y-%m-%d"),)

        result = database.fetch_query(sql, params=params, fetch_all=False)
        if result and result[0] is not None:
            return float(result[0])
        return 0.0

    def get_pengeluaran_per_kategori(self, tanggal: datetime.date | None = None) -> dict:
        """Mengelompokkan pengeluaran berdasarkan kategori (opsional filter tanggal)."""
        hasil = {}
        sql = "SELECT kategori, SUM(jumlah) FROM transaksi"
        params = []

        if tanggal:
            sql += " WHERE tanggal = ?"
            params.append(tanggal.strftime("%Y-%m-%d"))

        sql += " GROUP BY kategori HAVING SUM(jumlah) > 0 ORDER BY SUM(jumlah) DESC"

        rows = database.fetch_query(sql, params=tuple(params) if params else None, fetch_all=True)
        if rows:
            for row in rows:
                kategori = row['kategori'] if row['kategori'] else "Lainnya"
                jumlah = float(row[1]) if row[1] is not None else 0.0
                hasil[kategori] = jumlah
        return hasil

    def hapus_transaksi(self, id_transaksi: int) -> bool:
        """
        Menghapus transaksi dari database berdasarkan ID.
        Mengembalikan True jika penghapusan berhasil, False jika gagal.
        """
        if not isinstance(id_transaksi, int) or id_transaksi <= 0:
            print(f"Peringatan: ID transaksi '{id_transaksi}' tidak valid untuk dihapus.")
            return False

        sql = "DELETE FROM transaksi WHERE id = ?"
        params = (id_transaksi,)

        # Karena database.execute_query sekarang mengembalikan bool, kita bisa langsung menggunakannya.
        return database.execute_query(sql, params)