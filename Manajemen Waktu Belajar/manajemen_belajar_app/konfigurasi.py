# konfigurasi.py

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NAMA_DB = 'manajemen_belajar.db'
DB_PATH = os.path.join(BASE_DIR, NAMA_DB)

# Daftar mata kuliah
MATAKULIAH_PILIHAN = [
    "Teknik Digital",
    "Sistem Tertanam",
    "Bahasa Inggris",
    "Kewarganegaraan",
    "Sistem Basis Data II",
    "Kecerdasan Buatan",
    "Pemrograman Berorientasi Objek",
    "Jaringan Komputer I",
    "Statistika",
    "Lainnya"
]
MATAKULIAH_DEFAULT = "Lainnya"
TINGKAT_PEMAHAMAN_PILIHAN = ["Rendah", "Sedang", "Tinggi", "Sangat Tinggi"]
TINGKAT_PEMAHAMAN_DEFAULT = "Sedang"