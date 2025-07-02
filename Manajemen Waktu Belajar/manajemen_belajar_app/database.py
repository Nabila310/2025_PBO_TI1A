# database.py

import sqlite3
import pandas as pd
from konfigurasi import DB_PATH

def get_db_connection() -> sqlite3.Connection | None:
    """Membuka dan mengembalikan koneksi baru ke database SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"ERROR [database.py] Koneksi DB gagal: {e}")
        return None

def execute_query(query: str, params: tuple = None):
    """
    Menjalankan query non-SELECT (seperti INSERT, UPDATE, DELETE).
    Mengembalikan lastrowid jika INSERT, True jika DELETE/UPDATE berhasil, None jika gagal.
    """
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        
        if query.strip().upper().startswith("DELETE") or query.strip().upper().startswith("UPDATE"):
            return True if cursor.rowcount > 0 else False
        
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"ERROR [database.py] Query gagal: {e} | Query: {query[:60]}...")
        conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def fetch_query(query: str, params: tuple = None, fetch_all: bool = True):
    """Menjalankan query SELECT dan mengembalikan hasil."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall() if fetch_all else cursor.fetchone()
        return result
    except sqlite3.Error as e:
        print(f"ERROR [database.py] Fetch gagal: {e} | Query: {query[:60]}...")
        return None
    finally:
        if conn:
            conn.close()

def get_dataframe(query: str, params: tuple = None) -> pd.DataFrame:
    """Menjalankan query SELECT dan mengembalikan hasil sebagai DataFrame Pandas."""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()

    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        print(f"ERROR [database.py] Gagal baca ke DataFrame: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def setup_database_initial():
    """
    Memastikan tabel 'sesi_belajar' ada.
    Dipanggil oleh ManajerBelajar jika perlu (opsional setup awal).
    """
    print(f"Memeriksa/membuat tabel di database (via database.py): {DB_PATH}")
    conn = get_db_connection()
    if not conn:
        return False

    try:
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
        cursor.execute(sql_create_table)
        conn.commit()
        print(" -> Tabel 'sesi_belajar' siap.")
        return True
    except sqlite3.Error as e:
        print(f"Error SQLite saat setup tabel: {e}")
        return False
    finally:
        if conn:
            conn.close()