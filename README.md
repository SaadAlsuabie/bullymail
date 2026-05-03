# BullyMail — Email Bullying Detection

A Flask web app that flags potentially bullying language in email text, with an academic / university-email focus. It combines **TF–IDF + machine learning** (logistic regression or linear SVM) with **phrase-based rules**, stores results in **MySQL**, and can **connect to Gmail** over IMAP/SMTP for fetch and test sends.

## Features

- Paste-or-fetch email analysis with confidence and rule matches  
- Train models on synthetic datasets (bullying / supportive / neutral templates) and export Excel datasets  
- Dashboard for stats, history, model training, and optional Gmail integration (app password)

## Requirements

- Python 3.8+  
- MySQL with a database named `bullymail_db` (or adjust config)  
- NLTK data downloads on first run (`punkt`, `stopwords`)

## Setup

1. **MySQL** — Create the database and user, or import `database_setup.sql` if you use that dump. The app also creates tables on startup via `init_database()` in `app.py`.

2. **Database credentials** — Edit the `Config.DB_CONFIG` block in `app.py` (`host`, `user`, `password`, `database`). Defaults assume `localhost`, user `root`, password `root`, database `bullymail_db`.

3. **Python dependencies** (no `requirements.txt` in repo; install equivalents):

   ```bash
   pip install flask flask-cors mysql-connector-python pandas numpy nltk scikit-learn joblib openpyxl faker
   ```

## Run

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000). The landing page links to login and the dashboard.

**Default demo login** (change before any real deployment): `admin` / `admin123` — printed in the console on startup.

## Project layout

| Path | Role |
|------|------|
| `app.py` | Flask app, ML pipeline, email integration, API routes |
| `database_setup.sql` | Optional MySQL schema / sample data |
| `templates/` | `index.html`, `login.html`, `dashboard.html` |
| `saved_models/` | Created at runtime for `joblib` models |
| `datasets/` | Created at runtime for generated `.xlsx` files |

## Disclaimer

Automated detection can misclassify text and is not a substitute for human judgment, policy, or professional support.
