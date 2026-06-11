# Book Review Web Application — Flask, PostgreSQL, Google Books API

*CMPSC 297 — Special Topics · The Pennsylvania State University · 2023*

**[Live Showcase →](https://halkhoori2000.github.io/Book-Review-Web-Application/)**

A full-stack book review platform where users register, search a database of 5,000 books by title, author, or ISBN, write star-rated reviews, and access book metadata enriched from the Google Books API. Each user can post one review per book. A JSON API endpoint exposes book data and aggregate review statistics for external consumption.

Built with Flask on the backend, PostgreSQL as the relational store, and Bootstrap 5 for the UI. HTML is generated directly in Python via f-string view functions — no Jinja templates. Sessions are managed server-side with Flask-Session. The database schema is three tables (Books, Users, Reviews) with FK constraints, seeded from a 5,000-row CSV via a standalone import script.


---

## Use Cases
- Book discovery: users search across 5,000 titles by title, author, or ISBN partial match — useful as a personal reading tracker or library catalogue
- Crowd-sourced reviews: each logged-in user contributes one review and a 1–5 score per book; the page aggregates all reviews so readers can compare opinions
- External data enrichment: every book page pulls live average rating and ratings count from the Google Books API, blending local user reviews with global data
- API integration: the `/api/<isbn>` endpoint returns JSON with title, author, year, ISBN, review count, and average score — making the local database consumable by any frontend or script
- Auth-gated access: all book and search pages require login; the registration and login flow is fully integrated with PostgreSQL user management

## Challenges
- **No ORM — raw psycopg2**: all queries are written as explicit SQL strings with parameterised inputs to prevent injection; connection is established once at startup inside a `with` block and shared across routes — this means any lost connection requires a server restart rather than automatic reconnection
- **One-time review enforcement**: enforced at the query level (`SELECT COUNT(*) FROM reviews WHERE postedby = %s AND reviewof = %s`) rather than a DB constraint — a UNIQUE constraint on (postedby, reviewof) would be more robust and eliminate the extra round-trip
- **Plaintext passwords**: user passwords are stored as-is in the Users table; a production system would use bcrypt or Argon2 with a per-user salt before storing
- **Inline HTML generation**: all view functions return raw f-string HTML, making the codebase harder to maintain at scale — a Jinja2 template layer would separate logic from presentation and support partial re-renders

---

## Tech Stack

| Item | Detail |
|---|---|
| Backend | Python · Flask |
| Database | PostgreSQL · psycopg2-binary |
| ORM / Query | Raw SQL with parameterised queries |
| Sessions | Flask-Session (filesystem-backed) |
| External API | Google Books API v1 |
| UI | Bootstrap 5 |
| Data | 5,000-book CSV seed (`books.csv`) |

---

## Project Structure

```
Book-Review-Web-Application/
├── src/
│   ├── application.py      ← Flask app: routes, view functions, DB queries
│   ├── requirements.txt    ← Python dependencies
│   ├── books.csv           ← 5,000-book seed dataset
│   ├── sampleAPI.py        ← Example script consuming /api/<isbn>
│   └── db/
│       ├── queries.sql     ← Schema: Books, Users, Reviews tables + FK constraints
│       ├── import.py       ← Seed script: reads books.csv → inserts into Books table
│       └── books.csv       ← Book data for seeding
└── index.html              ← GitHub Pages project showcase
```

---

## Run

**Requirements:** Python 3.8+, PostgreSQL running locally.

```bash
# 1. Set up the database
psql -U postgres
\i src/db/queries.sql      # creates 'books' DB and all tables

# 2. Seed books data
python3 src/db/import.py   # inserts 5,000 rows from books.csv

# 3. Install dependencies
pip install -r src/requirements.txt

# 4. Update DB credentials in src/application.py (line 30–33):
#    database='books', user='postgres', password='<yours>', host='localhost', port='5432'

# 5. Start the server
python3 src/application.py
# Open http://localhost:5000
```

**API endpoint:**
```
GET /api/<isbn>
→ { "title": "...", "author": "...", "year": ..., "isbn": "...", "review_count": ..., "average_score": ... }
```

---

## Course

The Pennsylvania State University
