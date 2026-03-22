"""
analytics.py - Statistiques CENAD SANS pandas/matplotlib
Calculs purs Python + SQLite — compatible Android léger
"""

import os
from db_manager import get_connection


def compute_stats():
    """Calcule toutes les statistiques descriptives (Python pur)."""
    conn = get_connection()
    stats = {}

    stats['total'] = conn.execute("SELECT COUNT(*) FROM membres").fetchone()[0]

    rows = conn.execute("SELECT sexe, COUNT(*) FROM membres GROUP BY sexe").fetchall()
    stats['par_sexe'] = {r[0]: r[1] for r in rows}

    rows = conn.execute("SELECT niveau, COUNT(*) FROM membres GROUP BY niveau ORDER BY niveau").fetchall()
    stats['par_niveau'] = {r[0]: r[1] for r in rows}

    rows = conn.execute("SELECT batiment, COUNT(*) FROM membres GROUP BY batiment ORDER BY batiment").fetchall()
    stats['par_batiment'] = {r[0]: r[1] for r in rows}

    rows = conn.execute("SELECT promotion, COUNT(*) FROM membres GROUP BY promotion ORDER BY promotion DESC").fetchall()
    stats['par_promotion'] = {r[0]: r[1] for r in rows}

    rows = conn.execute("SELECT etablissement, COUNT(*) FROM membres GROUP BY etablissement ORDER BY COUNT(*) DESC").fetchall()
    stats['par_etablissement'] = {r[0]: r[1] for r in rows}

    conn.close()

    # Stats NumPy remplacées par Python pur
    if stats['total'] > 0:
        values = list(stats['par_niveau'].values())
        if values:
            stats['niveau_mean'] = sum(values) / len(values)
            mean = stats['niveau_mean']
            stats['niveau_std'] = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
            stats['niveau_max'] = max(values)

    return stats


def export_csv():
    """Exporte tous les membres en CSV (Python pur, sans pandas)."""
    import csv
    path = os.path.join(os.path.dirname(__file__), 'data', 'export_membres.csv')
    conn = get_connection()
    rows = conn.execute("SELECT * FROM membres ORDER BY nom").fetchall()
    conn.close()

    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
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
