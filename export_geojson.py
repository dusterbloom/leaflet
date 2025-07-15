#!/usr/bin/env python3
"""
export_geojson.py
Converts official CSV → SQLite → wind.geojson
Usage:  python export_geojson.py official.csv
"""
import sqlite3, csv, json, sys
from pathlib import Path

CSV_FILE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('wind_farms_sardinia.csv')
DB_FILE  = Path('wind.db')
GEO_FILE = Path('wind.geojson')

# 1. CSV → SQLite
with sqlite3.connect(DB_FILE) as conn:
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS wind")
    cur.execute("""
        CREATE TABLE wind (
            company      TEXT,
            name         TEXT,
            type         TEXT,
            municipality TEXT,
            mw           REAL,
            lat          REAL,
            lon          REAL,
            height       REAL,
            diameter     REAL,
            procedure    TEXT
        )
    """)
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute(
                "INSERT INTO wind VALUES (?,?,?,?,?,?,?,?,?,?)",
                (
                    row['Proponente'] or 'N/A',
                    row['Nome Progetto'] or 'N/A',
                    row['Tipo'] or 'ONSHORE',
                    row['Localita'] or 'N/A',
                    float(row['MWp'] or 0),
                    float(row['Lat Converted'] or 0),
                    float(row['Long Converted'] or 0),
                    float(row['Altezza Totale'] or 0),
                    float(row['Diametro'] or 0),
                    row['Procedura'] or 'N/A'
                )
            )
    conn.commit()

# 2. SQLite → GeoJSON
features = []
with sqlite3.connect(DB_FILE) as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM wind")
    for row in cur.fetchall():
        company,name,type_,municipality,mw,lat,lon,height,diameter,procedure = row
        if lat and lon:
            features.append({
                "type": "Feature",
                "properties": {
                    "company": company,
                    "name": name,
                    "type": type_,
                    "municipality": municipality,
                    "mw": mw,
                    "height": height,
                    "diameter": diameter,
                    "procedure": procedure
                },
                "geometry": {"type": "Point", "coordinates": [lon, lat]}
            })

with open(GEO_FILE, 'w', encoding='utf-8') as f:
    json.dump({"type": "FeatureCollection", "features": features}, f, ensure_ascii=False, indent=2)

print(f"✅ {GEO_FILE} scritto con {len(features)} progetti.")