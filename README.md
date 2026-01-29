# CS50-Price

CS50-Price is a crowdsourced web app for collecting and exploring real-world product prices (and optional quality notes) from shops across Bangladesh.

It’s built for “normal people”: log in, submit what you paid, and browse nearby reports on a map.

## What you can do

- Submit **price reports** (shop + product + price + quantity)
- Add an optional **quality report** for the same purchase (category-specific scoring)
- **Browse by location**: choose a category/product, set your location on a map, and find nearby reports
- Propose new **shops** and **product aliases** (admin-reviewed)
- Admins can **approve/reject** shop proposals and product-alias proposals

## How it works (quick tour)

1. **Register / Login**
2. **Contribute**
	- Propose a shop (uses a map to capture latitude/longitude)
	- Propose a product alias (maps a common name to a canonical product)
	- Submit a price report
	- (Optional) Add a quality report tied to your price report
3. **Browse**
	- Pick category → product → location → distance
	- The app returns nearby results and can optionally **group results by shop** with aggregated stats

## Tech stack

- **Backend:** Flask
- **Database:** SQLite (`app.db`) via `cs50` SQL helper
- **Sessions:** `Flask-Session` (filesystem)
- **UI:** Bootstrap + Bootstrap Icons
- **Maps:** Leaflet + OpenStreetMap tiles

## Project structure

- `app.py` — Flask app entry point (registers blueprints)
- `routes/` — route blueprints
  - `auth.py` — login/register/logout
  - `user.py` — user features (create reports, browse, API endpoints)
  - `admin.py` — admin review actions
- `templates/` — Jinja2 templates
- `static/` — CSS/JS
- `schema.sql` — SQLite schema

## Setup (Windows / PowerShell)

Prereqs:
- Python 3 installed
- `sqlite3` installed (or use DB Browser for SQLite)

From the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run the app:

```powershell
$env:FLASK_APP = "app.py"
$env:FLASK_DEBUG = "1"
flask run
```

Then open `http://127.0.0.1:5000/`.

## Common pages

- `/register` — create an account
- `/login` — sign in
- `/create/price_report` — submit a price report
- `/browse/price_reports` — browse nearby reports by location
- `/user/price_reports` — your submissions (and the quality report link)

## Admin notes

Admins can review proposals (shops, product aliases). The admin UI is available once your user has `user_type = 'admin'`.

If you need to promote a user manually:

```sql
UPDATE users SET user_type = 'admin' WHERE username = 'your_username';
```

## Data model (high-level)

- `products` — canonical products (with category)
- `product_aliases` — alternate names tied to canonical products
- `shops` — approved shop list (with latitude/longitude)
- `price_reports` — reported purchases
- `quality_reports` + category tables — optional quality scoring linked to a price report
- `shop_proposals` / `product_alias_proposals` — pending items for admin review

## Credits

Created as a CS50x final project.
