### 🧠 **Role:** Full‑Stack Geo Data & Civic Engagement Engineer

---

## 🎯 **Objective**

Implement a complete, production-ready interactive Sardinia wind farm map—**single HTML file** + **Python/SQLite export script**—leveraging `leaflet-geojson-vt` for vector tile rendering.

---

## 1. **Data Handling & Pipeline**

* Provide `export_geojson.py`:

  * Imports **official CSV**, normalizes fields, inserts into SQLite.
  * Exports `wind.geojson` (FeatureCollection with properties: proponente, nome\_progetto, tipo, localita, mwp, lat, lon, altezza, diametro, procedura).
* Use GeoJSON hosted on GitHub Pages (`wind.geojson`).

---

## 2. **Map & Rendering**

* Include CDN for Leaflet.js, MarkerCluster, PapaParse, geojson‑vt, and leaflet-geojson-vt.
* Load GeoJSON and use `L.geoJson.vt(geojson, { ... })` for vector-tiled rendering.

  * Options: `maxZoom`, `tolerance`, **dynamic styling** by feature type.
* Clustering optional if needed, but vt layer should support \~2,500 points efficiently.

---

## 3. **Feature Popups & Sharing**

* Circle markers colored green (onshore) / blue (offshore).
* Popup content includes:

  * Project name, municipality, MW, height, rotor diameter, proponent.
  * "Take Action" **mailto** button with pre-filled email in Italian + English.
  * Social share links (WhatsApp and Twitter) including `?lat=&lon=&zoom=` URL.
  * **Copy coordinates** button.

---

## 4. **UI, Filters & Stats**

* Bilingual toggle (IT/EN): swaps UI text, stats, banner.
* Filter buttons: All / Onshore / Offshore.
* Search input (project name or municipality).
* Real-time stats: visible projects count & total MW.
* Button to download **visible** as CSV.

---

## 5. **Proximity Tool & Sidebar**

* Include **proximity slider** (1–50 km).
* Clicking marker:

  * Calculates nearby projects (excluding itself) within slider distance using Haversine.
  * Populates **sidebar list** (name, municipality, MW).
  * Clicking list item centers map on that marker and opens its popup.

---

## 6. **Visibility Circles**

* Toggle to show circles (\~30×height in meters, default 5 km) around each visible marker.

---

## 7. **Responsive & Performance**

* Mobile-responsive layout with collapsible sidebar on small screens.
* Include `console.log()` for debugging pipeline, vt loading, tile stats.
* Inline comments explaining vt settings, Haversine, mailto/template.

---

## ✅ **Deliverables**

1. `index.html`—fully working, copy-pasteable.
2. `export_geojson.py`—produces `wind.geojson` from CSV.

---

### 🛠 **Don't ask; just produce**

* Full code for both files.
* Use `leaflet-geojson-vt` correctly with dynamic styling and click events.
* Integrate all features listed above.
* Ensure hosted on GitHub Pages works out of the box.