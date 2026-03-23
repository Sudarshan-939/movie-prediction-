# 🎬 CineScore — Movie Rating Prediction

An AI-powered web application that predicts IMDb movie ratings using an OMDB API-powered data pipeline and a Gradient Boosting ML model.

---

## Project Structure

```
movie-project/
│
├── backend/
│   ├── app.py           ← Flask REST API + ML model
│   ├── model.pkl        ← Auto-generated on first run
│   └── requirements.txt
│
├── frontend/
│   └── app.py           ← Streamlit UI
│
├── data/
│   └── dataset.csv      ← Training dataset (50 movies)
│
└── README.md
```

---

## Quick Start

### 1 — Install dependencies

```bash
cd movie-project/backend
pip install -r requirements.txt
pip install streamlit
```

### 2 — Start the Flask backend

```bash
# From movie-project/backend/
python app.py
```
Flask runs on **http://localhost:5000**. The model trains automatically on first boot.

### 3 — Start the Streamlit frontend

```bash
# From movie-project/frontend/
streamlit run app.py
```
Opens on **http://localhost:8501**

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Model status + accuracy metrics |
| GET | `/api/search?title=<query>` | Search movies by title |
| GET | `/api/predict?imdb_id=<id>` | Full prediction + OMDB metadata |
| POST | `/api/retrain` | Force model retraining |

---

## ML Model

- **Algorithm:** Gradient Boosting Regressor (scikit-learn)
- **Features:** Runtime, Metascore, Log(Votes), Genre Quality Score, Movie Age
- **Target:** IMDb Rating (1–10)
- **OMDB API Key:** `40fd4e23`
