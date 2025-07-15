# AGENTS.md

## Build/Lint/Test Commands
- **Serve locally**: `python serve.py [port]` - starts HTTP server on port 8000
- **Generate data**: `python data/export_geojson.py` - creates wind.geojson from CSV
- **No formal tests** - manual testing via browser at http://localhost:8000
- **No linting** - use browser dev tools for JS/HTML validation

## Code Style Guidelines
- **HTML**: Single quotes for attributes, semantic HTML5, responsive design
- **CSS**: Single-line for simple rules, BEM-like naming, mobile-first responsive
- **JS**: ES6+, camelCase variables, const/let preferred, semicolons required
- **Python**: PEP 8, snake_case, type hints, docstrings for functions
- **Imports**: Standard library first, third-party second, local last
- **Error handling**: Try/catch for data loading, graceful fallbacks
- **Naming**: Italian/English bilingual support, descriptive variable names
- **Data**: GeoJSON format, properties in English (company, name, type, etc.)