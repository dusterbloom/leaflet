import csv
import json
import sqlite3
import os
import re

def clean_numeric_string(s):
    """
    Cleans a string to make it a valid float representation.
    It handles decimal commas, multiple decimal points, and spaces.
    """
    if not isinstance(s, str):
        return str(s) if isinstance(s, (int, float)) else None
    
    s = s.strip()
    if not s:
        return None
    
    # Handle spaces in numbers like "6 .8"
    s = s.replace(' ', '')
    
    # Replace comma with dot for decimal separator
    s = s.replace(',', '.')
    
    # If multiple dots are present, keep the first one and remove the rest
    if s.count('.') > 1:
        parts = s.split('.')
        s = parts[0] + '.' + ''.join(parts[1:])
    
    # Remove any non-numeric characters except digits, dot, and minus
    import re as regex
    s = regex.sub(r'[^\d.-]', '', s)
    
    try:
        float(s)
        return s
    except ValueError:
        return None

def parse_dms_to_dd(coord_str):
    """
    Parses a coordinate string in various formats (DMS, Decimal Degrees)
    and converts it to a decimal degree float.
    Handles formats like: "39°42'27.75""N", "9.44954877", "9°11.340'E", "39°30’34.87"N".
    """
    if not isinstance(coord_str, str) or not coord_str.strip():
        return None

    coord_str = coord_str.strip()
    
    # Try direct float conversion first for simple decimal degrees
    try:
        return float(coord_str.replace(',', '.'))
    except ValueError:
        pass

    # Normalize special characters
    coord_str = coord_str.replace('’', "'").replace('`', "'").replace('"', '').replace('""', '').replace('”', "'")
    
    # More comprehensive DMS regex to handle various formats
    dms_patterns = [
        # Format: 39°30'34.87"N
        r'(?P<deg>\d{1,3})[°d\s]+(?P<min>\d{1,2})[\'m′\s]+(?P<sec>\d{1,2}(?:\.\d+)?)["s″\s]*(?P<dir>[NSEW])',
        # Format: 39°30'34.87 (without direction)
        r'(?P<deg>\d{1,3})[°d\s]+(?P<min>\d{1,2})[\'m′\s]+(?P<sec>\d{1,2}(?:\.\d+)?)["s″\s]*',
        # Format: 39°30.58'N (decimal minutes)
        r'(?P<deg>\d{1,3})[°d\s]+(?P<min>\d{1,2}(?:\.\d+)?)[\'m′\s]*(?P<dir>[NSEW])',
        # Format: 39°30.58' (decimal minutes without direction)
        r'(?P<deg>\d{1,3})[°d\s]+(?P<min>\d{1,2}(?:\.\d+)?)[\'m′\s]*',
        # Format: 39°30'37.16" (with seconds but no direction)
        r'(?P<deg>\d{1,3})[°d\s]+(?P<min>\d{1,2})[\'m′\s]+(?P<sec>\d{1,2}(?:\.\d+)?)["s″\s]*',
    ]
    
    for pattern in dms_patterns:
        match = re.search(pattern, coord_str, re.IGNORECASE)
        if match:
            parts = match.groupdict()
            degrees = float(parts.get('deg', 0))
            minutes = float(parts.get('min', 0))
            seconds = float(parts.get('sec', 0)) if parts.get('sec') else 0
            direction = parts.get('dir', '').upper()
            
            dd = degrees + minutes / 60.0 + seconds / 3600.0
            
            if direction in ('S', 'W'):
                dd *= -1
            
            return dd
    
    return None

def create_database_and_import_csv(db_path, csv_path):
    """
    Creates an SQLite database and imports data from the provided CSV file,
    normalizing and cleaning the data during the process.
    """
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("Database created and connection opened.")

    cursor.execute('''
    CREATE TABLE wind_projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proponente TEXT,
        nome_progetto TEXT,
        tipo TEXT,
        localita TEXT,
        mwp REAL,
        lat REAL,
        lon REAL,
        altezza INTEGER,
        diametro INTEGER,
        procedura TEXT
    )
    ''')
    print("Table 'wind_projects' created.")

    try:
        with open(csv_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            insert_sql = '''
            INSERT INTO wind_projects (proponente, nome_progetto, tipo, localita, mwp, lat, lon, altezza, diametro, procedura)
            VALUES (:proponente, :nome_progetto, :tipo, :localita, :mwp, :lat, :lon, :altezza, :diametro, :procedura)
            '''
            
            count = 0
            skipped = 0
            for row in reader:
                data_to_insert = {
                    'proponente': row.get('Proponente', '').strip(),
                    'nome_progetto': row.get('Nome Progetto', '').strip(),
                    'localita': row.get('Localita', '').strip(),
                    'procedura': row.get('Procedura', '').strip()
                }

                # Clean and convert numeric fields using the new helper function
                mwp_str = clean_numeric_string(row.get('MWp', '0'))
                data_to_insert['mwp'] = float(mwp_str) if mwp_str else None

                altezza_str = clean_numeric_string(row.get('Altezza Totale', '0'))
                try:
                    data_to_insert['altezza'] = int(float(altezza_str)) if altezza_str else None
                except (ValueError, TypeError):
                    data_to_insert['altezza'] = None

                diametro_str = clean_numeric_string(row.get('Diametro', '0'))
                try:
                    data_to_insert['diametro'] = int(float(diametro_str)) if diametro_str else None
                except (ValueError, TypeError):
                    data_to_insert['diametro'] = None
                
                # Normalize 'Tipo' field
                tipo_raw = row.get('Tipo', '').lower()
                if 'offshore' in tipo_raw or 'off-shore' in tipo_raw:
                    data_to_insert['tipo'] = 'offshore'
                else:
                    data_to_insert['tipo'] = 'onshore'

                # Parse and convert coordinates - handle both decimal degrees and DMS
                lat_raw = row.get('Lat_Converted', '').strip()
                lon_raw = row.get('Long_Converted', '').strip()
                
                # Try DMS parsing first, then decimal degrees
                lat_val = parse_dms_to_dd(lat_raw)
                if lat_val is None:
                    # Try direct decimal degrees
                    try:
                        lat_val = float(clean_numeric_string(lat_raw))
                    except (ValueError, TypeError):
                        lat_val = None
                
                lon_val = parse_dms_to_dd(lon_raw)
                if lon_val is None:
                    # Try direct decimal degrees
                    try:
                        lon_val = float(clean_numeric_string(lon_raw))
                    except (ValueError, TypeError):
                        lon_val = None
                
                # Validate coordinates are within reasonable ranges for Sardinia
                if lat_val is not None and lon_val is not None:
                    # Sardinia coordinates: roughly 38.5-41.5°N, 8-10°E
                    if 38 <= lat_val <= 42 and 8 <= lon_val <= 10.5:
                        data_to_insert['lat'] = lat_val
                        data_to_insert['lon'] = lon_val
                        cursor.execute(insert_sql, data_to_insert)
                        count += 1
                    else:
                        # Skip UTM coordinates and other invalid formats
                        skipped += 1
                        if lat_val > 1000 or lon_val > 1000:
                            print(f"Skipping row for project '{data_to_insert['nome_progetto']}' - appears to be UTM coordinates: lat={lat_val}, lon={lon_val}")
                        else:
                            print(f"Skipping row for project '{data_to_insert['nome_progetto']}' - coordinates outside Sardinia: lat={lat_val}, lon={lon_val}")
                else:
                    skipped += 1
                    print(f"Skipping row for project '{data_to_insert['nome_progetto']}' due to invalid coordinates: lat='{lat_raw}', lon='{lon_raw}'")

            conn.commit()
            print(f"\nSuccessfully imported and cleaned {count} records.")
            if skipped > 0:
                print(f"Skipped {skipped} records due to invalid data.")

    except FileNotFoundError:
        print(f"Error: The file {csv_path} was not found.")
        conn.close()
        return None
    except Exception as e:
        print(f"An error occurred during CSV import: {e}")
        conn.rollback()
        conn.close()
        return None

    return conn

def export_to_geojson(conn, output_path):
    """
    Queries the database and exports the data as a GeoJSON FeatureCollection.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT proponente, nome_progetto, tipo, localita, mwp, lat, lon, altezza, diametro, procedura FROM wind_projects")
    
    features = []
    rows = cursor.fetchall()
    
    if not rows:
        print("No data found in the database to export.")
        return

    columns = [description[0] for description in cursor.description]

    for row in rows:
        row_dict = dict(zip(columns, row))
        
        if row_dict.get('lat') is not None and row_dict.get('lon') is not None:
            feature = {
                "type": "Feature",
                "properties": row_dict,
                "geometry": {
                    "type": "Point",
                    "coordinates": [row_dict['lon'], row_dict['lat']]
                }
            }
            features.append(feature)

    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }

    try:
        with open(output_path, 'w', encoding='utf-8') as outfile:
            json.dump(feature_collection, outfile, indent=2)
        print(f"Successfully exported {len(features)} features to {output_path}.")
    except Exception as e:
        print(f"Failed to write GeoJSON file: {e}")

    conn.close()
    print("Database connection closed.")

if __name__ == "__main__":
    # --- Configuration ---
    CSV_FILE = 'wind_farms_sardinia.csv'
    DB_FILE = 'wind_data.sqlite'
    GEOJSON_FILE = 'wind.geojson'
    
    # --- Main execution pipeline ---
    if not os.path.exists(CSV_FILE):
        print(f"ERROR: '{CSV_FILE}' not found. Please place the CSV file in the same directory as the script.")
    else:
        db_connection = create_database_and_import_csv(DB_FILE, CSV_FILE)
        if db_connection:
            export_to_geojson(db_connection, GEOJSON_FILE)