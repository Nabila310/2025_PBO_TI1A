import sqlite3
import os
from konfigurasi import DB_PATH

def setup_database():
    print(f"Memeriksa/membuat database di: {DB_PATH}")
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        sql_create_table = """
        CREATE TABLE IF NOT EXISTS sesi_belajar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mata_kuliah TEXT NOT NULL,
            topik TEXT NOT NULL,
            durasi_menit REAL NOT NULL CHECK(durasi_menit > 0),
            tanggal DATE NOT NULL,
            tingkat_pemahaman TEXT
        );
        """
        print("Membuat tabel 'sesi_belajar' (jika belum ada)...")
        cursor.execute(sql_create_table)
        conn.commit()
        print(" -> Tabel 'sesi_belajar' siap.")
        return True
    except sqlite3.Error as e:
        print(f" -> Error SQLite saat setup: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("--- Memulai Setup Database Manajemen Belajar ---")
    if setup_database():
        print(f"\nSetup database '{os.path.basename(DB_PATH)}' selesai.")
    else:
        print("\nSetup database GAGAL.")
    print("--- Setup Database Selesai ---")