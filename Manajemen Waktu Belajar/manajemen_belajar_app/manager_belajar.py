# manager_belajar.py

import datetime
import pandas as pd
from model import SesiBelajar
import database
from konfigurasi import MATAKULIAH_DEFAULT, TINGKAT_PEMAHAMAN_PILIHAN

class ManajerBelajar:
    """Mengelola logika bisnis sesi belajar (Repository Pattern)."""

    _db_setup_done = False

    def __init__(self):
        if not ManajerBelajar._db_setup_done:
            print("[ManajerBelajar] Melakukan pengecekan/setup database awal...")
            if database.setup_database_initial():
                ManajerBelajar._db_setup_done = True
                print("[ManajerBelajar] Database siap.")
            else:
                print("[ManajerBelajar] KRITIKAL: Setup database awal GAGAL!")

    def tambah_sesi_belajar(self, sesi: SesiBelajar) -> bool:
        """Menambahkan sesi belajar baru ke database."""
        if not isinstance(sesi, SesiBelajar) or sesi.durasi_menit <= 0:
            return False

        sql = "INSERT INTO sesi_belajar (mata_kuliah, topik, durasi_menit, tanggal, tingkat_pemahaman) VALUES (?, ?, ?, ?, ?)"
        params = (
            sesi.mata_kuliah,
            sesi.topik,
            sesi.durasi_menit,
            sesi.tanggal.strftime("%Y-%m-%d"),
            sesi.tingkat_pemahaman
        )

        last_id = database.execute_query(sql, params)
        if last_id is not None:
            sesi.id = last_id
            return True
        return False

    def hapus_sesi_belajar(self, id_sesi: int) -> bool:
        """
        Menghapus sesi belajar dari database berdasarkan ID.
        Mengembalikan True jika penghapusan berhasil, False jika gagal.
        """
        if not isinstance(id_sesi, int) or id_sesi <= 0:
            print(f"Peringatan: ID sesi '{id_sesi}' tidak valid untuk dihapus.")
            return False

        sql = "DELETE FROM sesi_belajar WHERE id = ?"
        params = (id_sesi,)

        return database.execute_query(sql, params)

    def get_semua_sesi_belajar_obj(self) -> list[SesiBelajar]:
        """Mengambil semua sesi belajar dari database dalam bentuk list SesiBelajar."""
        sql = "SELECT id, mata_kuliah, topik, durasi_menit, tanggal, tingkat_pemahaman FROM sesi_belajar ORDER BY tanggal DESC, id DESC"
        rows = database.fetch_query(sql, fetch_all=True)

        sesi_list = []
        if rows:
            for row in rows:
                sesi = SesiBelajar(
                    id_sesi=row['id'],
                    mata_kuliah=row['mata_kuliah'],
                    topik=row['topik'],
                    durasi_menit=row['durasi_menit'],
                    tanggal=row['tanggal'],
                    tingkat_pemahaman=row['tingkat_pemahaman']
                )
                sesi_list.append(sesi)
        return sesi_list

    def get_dataframe_sesi_belajar(self, filter_tanggal: datetime.date | None = None) -> pd.DataFrame:
        """Mengambil sesi belajar dalam bentuk DataFrame Pandas, bisa difilter berdasarkan tanggal."""
        query = "SELECT id, tanggal, mata_kuliah, topik, durasi_menit, tingkat_pemahaman FROM sesi_belajar"
        params = None

        if filter_tanggal:
            query += " WHERE tanggal = ?"
            params = (filter_tanggal.strftime("%Y-%m-%d"),)

        query += " ORDER BY tanggal DESC, id DESC"
        df = database.get_dataframe(query, params=params)

        if not df.empty:
            df.rename(columns={
                'id': 'ID',
                'mata_kuliah': 'Mata Kuliah',
                'topik': 'Topik',
                'durasi_menit': 'Durasi (Menit)',
                'tingkat_pemahaman': 'Pemahaman'
            }, inplace=True)
            df['Tanggal'] = pd.to_datetime(df['tanggal']).dt.strftime('%Y-%m-%d')
            df = df[['ID', 'Tanggal', 'Mata Kuliah', 'Topik', 'Durasi (Menit)', 'Pemahaman']]
        return df

    def hitung_total_durasi_belajar(self, tanggal: datetime.date | None = None) -> float:
        """Menghitung total durasi belajar (dalam menit) pada tanggal tertentu (atau seluruhnya jika tidak diberi tanggal)."""
        sql = "SELECT SUM(durasi_menit) FROM sesi_belajar"
        params = None

        if tanggal:
            sql += " WHERE tanggal = ?"
            params = (tanggal.strftime("%Y-%m-%d"),)

        result = database.fetch_query(sql, params=params, fetch_all=False)
        if result and result[0] is not None:
            return float(result[0])
        return 0.0

    def get_durasi_per_mata_kuliah(self, tanggal: datetime.date | None = None) -> dict:
        """Mengelompokkan durasi belajar berdasarkan mata kuliah (opsional filter tanggal)."""
        hasil = {}
        sql = "SELECT mata_kuliah, SUM(durasi_menit) FROM sesi_belajar"
        params = []

        if tanggal:
            sql += " WHERE tanggal = ?"
            params.append(tanggal.strftime("%Y-%m-%d"))

        sql += " GROUP BY mata_kuliah HAVING SUM(durasi_menit) > 0 ORDER BY SUM(durasi_menit) DESC"

        rows = database.fetch_query(sql, params=tuple(params) if params else None, fetch_all=True)
        if rows:
            for row in rows:
                matkul = row['mata_kuliah'] if row['mata_kuliah'] else MATAKULIAH_DEFAULT
                durasi = float(row[1]) if row[1] is not None else 0.0
                hasil[matkul] = durasi
        return hasil

    def get_distribusi_pemahaman_per_topik(self, tanggal: datetime.date | None = None) -> dict:
        """
        Menghitung distribusi tingkat pemahaman untuk setiap topik.
        Mengembalikan dictionary dengan topik sebagai kunci dan dictionary distribusi
        tingkat pemahaman sebagai nilai (e.g., {'Topik A': {'Rendah': 2, 'Sedang': 5}}).
        """
        hasil = {}
        sql = "SELECT topik, tingkat_pemahaman FROM sesi_belajar"
        params = []

        if tanggal:
            sql += " WHERE tanggal = ?"
            params.append(tanggal.strftime("%Y-%m-%d"))

        rows = database.fetch_query(sql, params=tuple(params) if params else None, fetch_all=True)

        if rows:
            for row in rows:
                topik = row['topik'] if row['topik'] else "Tidak Diketahui"
                pemahaman = row['tingkat_pemahaman'] if row['tingkat_pemahaman'] else "Tidak Diketahui"

                if topik not in hasil:
                    hasil[topik] = {level: 0 for level in TINGKAT_PEMAHAMAN_PILIHAN + ["Tidak Diketahui"]}
                hasil[topik][pemahaman] += 1
        return hasil