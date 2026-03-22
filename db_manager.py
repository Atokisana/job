"""
db_manager.py - Gestion SQLite CENAD avec import/export CSV
Compatible Android (chemin data adapté)
"""

import sqlite3
import hashlib
import os
import csv
from kivy.utils import platform

# Chemin adapté Android vs desktop
if platform == 'android':
    from android.storage import app_storage_path
    _DATA_DIR = os.path.join(app_storage_path(), 'data')
else:
    _DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

DB_PATH = os.path.join(_DATA_DIR, 'cenad.db')
ADMIN_PASSWORD_HASH = hashlib.sha256("cenad2024".encode()).hexdigest()


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=1000")
    return conn


def init_db():
    os.makedirs(_DATA_DIR, exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS membres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            sexe TEXT DEFAULT 'M',
            niveau TEXT DEFAULT 'L1',
            promotion TEXT,
            batiment TEXT,
            etablissement TEXT,
            commune_origine TEXT,
            telephone TEXT,
            photo TEXT DEFAULT ''
        )
    ''')
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nom ON membres(nom)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_promotion ON membres(promotion)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_batiment ON membres(batiment)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_niveau ON membres(niveau)")
    conn.commit()
    conn.close()


def insert_sample_data():
    conn = get_connection()
    cursor = conn.cursor()
    count = cursor.execute("SELECT COUNT(*) FROM membres").fetchone()[0]
    if count > 0:
        conn.close()
        return
    sample = [
        ("RAKOTO Jean", "M", "L2", "2022", "BLOC A", "ENSET", "Andapa", "0341234567", ""),
        ("RABE Marie", "F", "L3", "2021", "BLOC B", "ESP", "Andapa", "0349876543", ""),
        ("ANDRIANTSOA Paul", "M", "M1", "2020", "PJ A", "SCIENCES", "Andapa", "0345678901", ""),
        ("RAZAFY Hanta", "F", "L1", "2023", "BLOC H", "FLSH", "Sambava", "0342345678", ""),
        ("RAMAROSON Eric", "M", "M2", "2019", "PJ B", "AGRO", "Andapa", "0343456789", ""),
        ("RAKOTOMALALA Lina", "F", "L2", "2022", "BLOC A", "ENSET", "Andapa", "0344567890", ""),
        ("ANDRIAMAMPIANINA Solo", "M", "L3", "2021", "BLOC C", "DEGSP", "Doany", "0345678902", ""),
        ("RAVOLAHY Prisca", "F", "L1", "2023", "PJ B", "ISAE", "Andapa", "0346789013", ""),
        ("RAJAONARISON Mamy", "M", "M1", "2020", "BLOC A", "IST", "Andapa", "0347890124", ""),
        ("RANDRIAMANANTENA Fara", "F", "L2", "2022", "PV C", "ISISFA", "Bealanana", "0348901235", ""),
        ("RABEMANANTSOA Nivo", "M", "L3", "2021", "Belle rose", "ENSET", "Andapa", "0340123456", ""),
        ("RAKOTONDRABE Vola", "F", "M2", "2019", "BLOC G", "ESP", "Andapa", "0341234568", ""),
        ("ANDRIANARY Henintsoa", "M", "L1", "2023", "PJ C", "SCIENCES", "Tsaratanana", "0342345679", ""),
        ("RAZANAJATOVO Tiana", "F", "L2", "2022", "PV B", "AGRO", "Andapa", "0343456790", ""),
        ("RAKOTOARIVO Fidy", "M", "M1", "2020", "BLOC I", "FLSH", "Andapa", "0344567891", ""),
    ]
    cursor.executemany(
        "INSERT INTO membres (nom, sexe, niveau, promotion, batiment, etablissement, commune_origine, telephone, photo) VALUES (?,?,?,?,?,?,?,?,?)",
        sample
    )
    conn.commit()
    conn.close()


# ===== CRUD =====

def get_all_membres(limit=500, offset=0):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, nom, sexe, niveau, promotion, batiment, etablissement, photo FROM membres ORDER BY nom LIMIT ? OFFSET ?",
        (limit, offset)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_membres(query="", niveau="", promotion="", batiment="", etablissement=""):
    conn = get_connection()
    sql = "SELECT id, nom, sexe, niveau, promotion, batiment, etablissement, photo FROM membres WHERE 1=1"
    params = []
    if query:
        sql += " AND nom LIKE ?"
        params.append("%{}%".format(query))
    if niveau:
        sql += " AND niveau = ?"
        params.append(niveau)
    if promotion:
        sql += " AND promotion = ?"
        params.append(promotion)
    if batiment:
        sql += " AND batiment = ?"
        params.append(batiment)
    if etablissement:
        sql += " AND etablissement = ?"
        params.append(etablissement)
    sql += " ORDER BY nom LIMIT 500"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_membre_by_id(membre_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM membres WHERE id = ?", (membre_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_membre(data):
    conn = get_connection()
    conn.execute(
        "INSERT INTO membres (nom, sexe, niveau, promotion, batiment, etablissement, commune_origine, telephone, photo) VALUES (?,?,?,?,?,?,?,?,?)",
        (data['nom'], data['sexe'], data['niveau'], data.get('promotion', ''),
         data.get('batiment', ''), data.get('etablissement', ''), data.get('commune_origine', ''),
         data.get('telephone', ''), data.get('photo', ''))
    )
    conn.commit()
    conn.close()


def update_membre(membre_id, data):
    conn = get_connection()
    conn.execute(
        "UPDATE membres SET nom=?, sexe=?, niveau=?, promotion=?, batiment=?, etablissement=?, commune_origine=?, telephone=?, photo=? WHERE id=?",
        (data['nom'], data['sexe'], data['niveau'], data.get('promotion', ''),
         data.get('batiment', ''), data.get('etablissement', ''), data.get('commune_origine', ''),
         data.get('telephone', ''), data.get('photo', ''), membre_id)
    )
    conn.commit()
    conn.close()


def delete_membre(membre_id):
    conn = get_connection()
    conn.execute("DELETE FROM membres WHERE id = ?", (membre_id,))
    conn.commit()
    conn.close()


def get_stats_by_field(field):
    allowed = ['niveau', 'promotion', 'batiment', 'sexe', 'etablissement']
    if field not in allowed:
        return {}
    conn = get_connection()
    rows = conn.execute(
        "SELECT {}, COUNT(*) as total FROM membres GROUP BY {} ORDER BY total DESC".format(field, field)
    ).fetchall()
    conn.close()
    return {r[field]: r['total'] for r in rows}


def get_total_count():
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM membres").fetchone()[0]
    conn.close()
    return count


def verify_admin_password(password):
    return hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD_HASH


def get_distinct_values(field):
    allowed = ['niveau', 'promotion', 'batiment', 'etablissement']
    if field not in allowed:
        return []
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT {} FROM membres WHERE {} IS NOT NULL AND {} != '' ORDER BY {}".format(
            field, field, field, field)
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]


def export_csv():
    """Exporte tous les membres en CSV."""
    path = os.path.join(_DATA_DIR, 'cenad_membres.csv')
    conn = get_connection()
    rows = conn.execute("SELECT * FROM membres ORDER BY nom").fetchall()
    conn.close()

    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'nom', 'sexe', 'niveau', 'promotion',
                         'batiment', 'etablissement', 'commune_origine', 'telephone', 'photo'])
        for r in rows:
            writer.writerow([
                r['id'], r['nom'], r['sexe'], r['niveau'], r['promotion'],
                r['batiment'], r['etablissement'], r['commune_origine'],
                r['telephone'], r['photo']
            ])
    return path


def import_from_csv(csv_path):
    membres = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            nom = row.get('nom', '').strip()
            if not nom:
                continue
            membres.append((
                nom,
                row.get('sexe', 'M').strip(),
                row.get('niveau', 'L1').strip(),
                row.get('promotion', '').strip(),
                row.get('batiment', '').strip(),
                row.get('etablissement', '').strip(),
                row.get('commune_origine', '').strip(),
                row.get('telephone', '').strip(),
                row.get('photo', '').strip(),
            ))

    if not membres:
        raise ValueError("Aucun membre valide dans le fichier CSV")

    conn = get_connection()
    conn.execute("DELETE FROM membres")
    conn.executemany(
        "INSERT INTO membres (nom, sexe, niveau, promotion, batiment, etablissement, commune_origine, telephone, photo) VALUES (?,?,?,?,?,?,?,?,?)",
        membres
    )
    conn.commit()
    conn.close()
    return len(membres)


def import_from_zip(zip_path):
    import zipfile as zf
    import tempfile
    import shutil

    photos_dir = os.path.join(_DATA_DIR, 'photos')
    os.makedirs(photos_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        with zf.ZipFile(zip_path, 'r') as z:
            z.extractall(tmpdir)

        csv_path = None
        for root, dirs, files in os.walk(tmpdir):
            for f in files:
                if f.lower().endswith('.csv'):
                    csv_path = os.path.join(root, f)
                    break

        if not csv_path:
            raise ValueError("Aucun fichier CSV trouve dans le ZIP")

        photos_tmp = os.path.join(tmpdir, 'photos')
        if os.path.exists(photos_tmp):
            for fname in os.listdir(photos_tmp):
                src = os.path.join(photos_tmp, fname)
                dst = os.path.join(photos_dir, fname)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)

        membres = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                nom = row.get('nom', '').strip()
                if not nom:
                    continue
                photo_rel = row.get('photo', '').strip()
                if photo_rel:
                    fname = os.path.basename(photo_rel)
                    full_path = os.path.join(photos_dir, fname)
                    photo_final = full_path if os.path.exists(full_path) else ''
                else:
                    photo_final = ''

                membres.append((
                    nom,
                    row.get('sexe', 'M').strip(),
                    row.get('niveau', 'L1').strip(),
                    row.get('promotion', '').strip(),
                    row.get('batiment', '').strip(),
                    row.get('etablissement', '').strip(),
                    row.get('commune_origine', '').strip(),
                    row.get('telephone', '').strip(),
                    photo_final,
                ))

        if not membres:
            raise ValueError("Aucun membre valide dans le CSV")

        conn = get_connection()
        conn.execute("DELETE FROM membres")
        conn.executemany(
            "INSERT INTO membres (nom, sexe, niveau, promotion, batiment, etablissement, commune_origine, telephone, photo) VALUES (?,?,?,?,?,?,?,?,?)",
            membres
        )
        conn.commit()
        conn.close()
        return len(membres)
