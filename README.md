# BullyMail — Email Bullying Detection

A Flask web app that flags potentially bullying language in email text, with an academic / university-email focus. It combines **TF–IDF + machine learning** (logistic regression or linear SVM) with **phrase-based rules**, stores results in **MySQL** (falling back to a local **SQLite** file if MySQL is unavailable), and can **connect to Gmail** over IMAP/SMTP for fetch and test sends.

## Features

- Paste-or-fetch email analysis with confidence and rule matches
- PII masking (emails, phone numbers) applied before any text is analyzed or vectorized
- Train models on synthetic datasets (bullying / supportive / neutral templates) and export Excel datasets
- Dashboard for stats, history, model training, and optional Gmail integration (app password)
- Automatic SQLite fallback if MySQL isn't reachable — no manual setup required to try the app locally

## Requirements

- Python 3.8+
- MySQL with a database named `bullymail_db` (optional — the app falls back to a local `bullymail.db` SQLite file if MySQL isn't reachable)
- NLTK data downloads on first run (`punkt`, `stopwords`)

## Quickstart (from scratch)

These steps get the app running locally with **zero external dependencies** — no MySQL install needed, since the app automatically falls back to a local SQLite file.

1. **Clone the repo and enter the project folder**

   ```bash
   git clone https://github.com/SaadAlsuabie/bullymail.git
   cd bullymail/"Email Bullying Detection_Final_Code"
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate          # Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional) Set up MySQL** — only needed if you want persistent storage in MySQL instead of the default SQLite fallback:

   - Create a database and import the schema: `mysql -u root -p < database_setup.sql`
   - Edit the `Config.DB_CONFIG` block in `app.py` (`host`, `user`, `password`, `database`) to match your MySQL credentials. Defaults assume `localhost`, user `root`, password `root`, database `bullymail_db`.
   - If you skip this step entirely, the app detects MySQL is unreachable and automatically creates/uses a local `bullymail.db` SQLite file instead — no further action required.

5. **Run the app**

   ```bash
   python app.py
   ```

   On first run this also downloads NLTK's `punkt` and `stopwords` data automatically.

6. **Open the app** — go to [http://localhost:5000](http://localhost:5000). The landing page links to login and the dashboard.

7. **Log in** with the demo credentials (change before any real deployment): `admin` / `admin123` — also printed in the console on startup. The password is stored as a salted `scrypt` hash (via `werkzeug.security`), never in plaintext.

8. **(Optional) Generate a dataset and train a model** from the dashboard UI (Generate Dataset → Train Model), or run `python evaluate_model.py` for an offline evaluation — see [Model evaluation](#model-evaluation) below.

## Model evaluation

`evaluate_model.py` is a standalone script that trains and compares a Linear SVM and Logistic Regression model on `datasets/large_email_dataset.xlsx` (70/30 split), then writes evaluation plots and the best-performing model to disk. The dataset file ships in the repo, so this runs immediately after step 3 of the Quickstart above — no need to generate a dataset first:

```bash
python evaluate_model.py
```

Outputs:
- `static/confusion_matrix.png` — SVM confusion matrix
- `static/model_comparison.png` — accuracy/precision/recall/F1 comparison
- `saved_models/latest_model.joblib` and `saved_models/latest_vectorizer.joblib` — the higher-F1 model of the two

## Project layout

| Path | Role |
|------|------|
| `app.py` | Flask app, ML pipeline, email integration, API routes, MySQL/SQLite DB layer |
| `evaluate_model.py` | Standalone SVM vs. Logistic Regression evaluation + plotting script |
| `database_setup.sql` | Optional MySQL schema / sample data |
| `requirements.txt` | Python dependencies |
| `templates/` | `index.html`, `login.html`, `dashboard.html` |
| `saved_models/` | Created at runtime for `joblib` models |
| `datasets/` | Created at runtime for generated `.xlsx` files |

## Disclaimer

Automated detection can misclassify text and is not a substitute for human judgment, policy, or professional support.
