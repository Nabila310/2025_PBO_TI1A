# model.py

import datetime
import locale


class Transaksi:
    """Merepresentasikan satu entitas transaksi pengeluaran (Data Class)."""

    def __init__(self, deskripsi: str, jumlah: float, kategori: str, tanggal: datetime.date | str, id_transaksi: int | None = None):
        self.id = id_transaksi
        self.deskripsi = str(deskripsi) if deskripsi else "Tanpa Deskripsi"

        # Validasi dan konversi jumlah
        try:
            jumlah_float = float(jumlah)
            self.jumlah = jumlah_float if jumlah_float > 0 else 0.0
            if jumlah_float <= 0:
                print(f"Peringatan: Jumlah '{jumlah}' harus positif.")
        except (ValueError, TypeError):
            self.jumlah = 0.0
            print(f"Peringatan: Jumlah '{jumlah}' tidak valid.")

        # Kategori default
        self.kategori = str(kategori) if kategori else "Lainnya"

        # Validasi dan parsing tanggal
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
        try:
            locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
            jml_str = locale.format_string("%.0f", self.jumlah, grouping=True)
        except Exception:
            jml_str = f"{self.jumlah:.0f}"

        return (
            f"Transaksi(ID:{self.id}, Tgl:{self.tanggal.strftime('%Y-%m-%d')}, "
            f"Jml:{jml_str}, Kat:'{self.kategori}', Desc:'{self.deskripsi}')"
        )

    def to_dict(self) -> dict:
        """Mengonversi objek Transaksi ke format dictionary (untuk penyimpanan)."""
        return {
            "deskripsi": self.deskripsi,
            "jumlah": self.jumlah,
            "kategori": self.kategori,
            "tanggal": self.tanggal.strftime("%Y-%m-%d")
        }