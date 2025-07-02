# model.py

import datetime
import locale

class SesiBelajar:
    """Merepresentasikan satu entitas sesi belajar."""

    def __init__(self, mata_kuliah: str, topik: str, durasi_menit: float,
                 tanggal: datetime.date | str, tingkat_pemahaman: str = None,
                 id_sesi: int | None = None):
        self.id = id_sesi
        self.mata_kuliah = str(mata_kuliah).strip() if mata_kuliah else "Tanpa Mata Kuliah"
        self.topik = str(topik).strip() if topik else "Tanpa Topik"

        try:
            durasi_float = float(durasi_menit)
            self.durasi_menit = durasi_float if durasi_float > 0 else 0.0
            if durasi_float <= 0:
                print(f"Peringatan: Durasi '{durasi_menit}' harus positif.")
        except (ValueError, TypeError):
            self.durasi_menit = 0.0
            print(f"Peringatan: Durasi '{durasi_menit}' tidak valid.")

        self.tingkat_pemahaman = str(tingkat_pemahaman) if tingkat_pemahaman else "Tidak Diketahui"

        if isinstance(tanggal, datetime.date):
            self.tanggal = tanggal
        elif isinstance(tanggal, str):
            try:
                self.tanggal = datetime.datetime.strptime(tanggal, "%Y-%m-%d").date()
            except ValueError:
                self.tanggal = datetime.date.today()
                print(f"Peringatan: Format tanggal '{tanggal}' salah. Gunakan 'YYYY-MM-DD'.")
        else:
            self.tanggal = datetime.date.today()
            print(f"Peringatan: Tipe tanggal '{type(tanggal)}' tidak valid.")

    def __repr__(self) -> str:
        return (
            f"SesiBelajar(ID:{self.id}, Tgl:{self.tanggal.strftime('%Y-%m-%d')}, "
            f"Matkul:'{self.mata_kuliah}', Topik:'{self.topik}', "
            f"Durasi:{self.durasi_menit:.0f} menit, Pemahaman:'{self.tingkat_pemahaman}')"
        )

    def to_dict(self) -> dict:
        """Mengonversi objek SesiBelajar ke format dictionary (untuk penyimpanan)."""
        return {
            "mata_kuliah": self.mata_kuliah,
            "topik": self.topik,
            "durasi_menit": self.durasi_menit,
            "tanggal": self.tanggal.strftime("%Y-%m-%d"),
            "tingkat_pemahaman": self.tingkat_pemahaman
        }