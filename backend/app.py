"""
Movie Rating Prediction — Flask Backend (v2)
Multi-platform: IMDb (OMDB) + TMDB + Rotten Tomatoes + Metacritic
"""

import os, sys, json, math, joblib, requests
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, VotingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# ─────────────────────────────────────────────
#  Config
# ─────────────────────────────────────────────
OMDB_KEY   = "40fd4e23"
TMDB_KEY   = "d5b494541b4047bd371b2a041abc9859"
OMDB_BASE  = "http://www.omdbapi.com/"
TMDB_BASE  = "https://api.themoviedb.org/3"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
DATA_PATH  = os.path.join(os.path.dirname(__file__), "..", "data", "dataset.csv")

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────
#  Genre quality map
# ─────────────────────────────────────────────
GENRE_RANK = {
    "Documentary": 8.0, "Biography": 7.9, "Crime": 7.8, "History": 7.7,
    "Drama": 7.7, "Mystery": 7.5, "Thriller": 7.4, "War": 7.4,
    "Adventure": 7.2, "Animation": 7.2, "Western": 7.1, "Sci-Fi": 7.0,
    "Action": 6.9, "Fantasy": 6.8, "Romance": 6.6, "Comedy": 6.5,
    "Music": 6.5, "Horror": 5.9, "Sport": 6.8, "Family": 6.5,
}

def genre_score(s: str) -> float:
    if not s or s == "N/A": return 6.5
    parts = [g.strip() for g in s.split(",")]
    return round(sum(GENRE_RANK.get(g, 6.5) for g in parts) / len(parts), 2)

def safe_int(v, d=0):
    try: return int(str(v).replace(",", "").strip())
    except: return d

def safe_float(v, d=5.0):
    try: return float(str(v).replace(",", "").strip())
    except: return d

def parse_rt(s: str) -> float:
    """'87%' → 8.7  (scale to /10)"""
    try:
        return round(float(s.replace("%", "").strip()) / 10.0, 2)
    except:
        return 5.0

def parse_mc(s: str) -> float:
    """Metascore x/100 → /10"""
    try: return round(float(s) / 10.0, 2)
    except: return 5.5

# ─────────────────────────────────────────────
#  TMDB helpers
# ─────────────────────────────────────────────
def tmdb_find_by_imdb(imdb_id: str) -> dict:
    """Use TMDB /find to look up a movie by its IMDb ID."""
    try:
        r = requests.get(
            f"{TMDB_BASE}/find/{imdb_id}",
            params={"api_key": TMDB_KEY, "external_source": "imdb_id"},
            timeout=8,
        )
        hits = r.json().get("movie_results", [])
        return hits[0] if hits else {}
    except:
        return {}

def tmdb_details(tmdb_id: int) -> dict:
    """Full TMDB movie details."""
    try:
        r = requests.get(
            f"{TMDB_BASE}/movie/{tmdb_id}",
            params={"api_key": TMDB_KEY, "append_to_response": "credits,keywords"},
            timeout=8,
        )
        return r.json()
    except:
        return {}

def tmdb_search(title: str, year: str = None) -> dict:
    """Search TMDB by title."""
    params = {"api_key": TMDB_KEY, "query": title, "include_adult": False}
    if year:
        params["year"] = year
    try:
        r = requests.get(f"{TMDB_BASE}/search/movie", params=params, timeout=8)
        hits = r.json().get("results", [])
        return hits[0] if hits else {}
    except:
        return {}

TMDB_IMG = "https://image.tmdb.org/t/p/w500"

# ─────────────────────────────────────────────
#  Feature engineering
# ─────────────────────────────────────────────
def build_features(omdb: dict, tmdb: dict) -> np.ndarray:
    """
    Features (10):
      runtime, metascore_norm, rt_norm, tmdb_score,
      tmdb_popularity_log, votes_log, genre_score, age,
      tmdb_vote_count_log, budget_log
    """
    year     = safe_int(omdb.get("Year", "2000"), 2000)
    runtime  = safe_int(omdb.get("Runtime", "90 min").split()[0], 90)
    votes    = safe_int(omdb.get("imdbVotes", "100000"), 100000)

    # Metascore from OMDB
    metascore_raw = omdb.get("Metascore", "55")
    metascore     = parse_mc(metascore_raw) if metascore_raw != "N/A" else 5.5

    # Rotten Tomatoes from OMDB Ratings array
    rt_norm = 5.0
    for r in omdb.get("Ratings", []):
        if "Rotten Tomatoes" in r.get("Source", ""):
            rt_norm = parse_rt(r.get("Value", "50%"))
            break

    # TMDB
    tmdb_score       = safe_float(tmdb.get("vote_average", 6.5), 6.5)
    tmdb_votes       = safe_int(tmdb.get("vote_count", 1000), 1000)
    tmdb_popularity  = safe_float(tmdb.get("popularity", 10.0), 10.0)
    budget           = safe_int(tmdb.get("budget", 0), 0)

    gscore    = genre_score(omdb.get("Genre", ""))
    age       = 2025 - year
    vlog      = math.log1p(votes)
    tv_log    = math.log1p(tmdb_votes)
    tpop_log  = math.log1p(tmdb_popularity)
    budg_log  = math.log1p(budget)

    return np.array([[runtime, metascore, rt_norm, tmdb_score,
                      tpop_log, vlog, gscore, age, tv_log, budg_log]])

FEATURE_NAMES = [
    "runtime", "metascore_norm", "rt_norm", "tmdb_score",
    "tmdb_popularity_log", "votes_log", "genre_score", "age",
    "tmdb_vote_count_log", "budget_log",
]

# ─────────────────────────────────────────────
#  Model training
# ─────────────────────────────────────────────
def train_model():
    df = pd.read_csv(DATA_PATH)
    df["metascore"] = pd.to_numeric(df["metascore"], errors="coerce").fillna(55)
    df["rt_score"]  = pd.to_numeric(df["rt_score"],  errors="coerce").fillna(50)
    df.dropna(subset=["imdb_rating"], inplace=True)

    df["metascore_norm"]     = df["metascore"] / 10.0
    df["rt_norm"]            = df["rt_score"]  / 10.0
    df["votes_log"]          = df["votes"].apply(lambda v: math.log1p(safe_int(v)))
    df["tmdb_popularity_log"]= df["tmdb_popularity"].apply(lambda v: math.log1p(safe_float(v, 10)))
    df["age"]                = 2025 - df["year"].apply(lambda y: safe_int(y, 2000))
    df["genre_score"]        = df["genre"].apply(genre_score)
    df["tmdb_vote_count_log"]= df["votes"].apply(lambda v: math.log1p(safe_int(v) * 0.4))  # proxy
    df["budget_log"]         = 0.0  # not in CSV, will be fetched live

    feats = ["runtime", "metascore_norm", "rt_norm", "tmdb_score",
             "tmdb_popularity_log", "votes_log", "genre_score", "age",
             "tmdb_vote_count_log", "budget_log"]

    X = df[feats].values
    y = df["imdb_rating"].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    # Ensemble: GBR + RF + Ridge
    gbr = GradientBoostingRegressor(n_estimators=400, learning_rate=0.04, max_depth=4, random_state=42)
    rf  = RandomForestRegressor(n_estimators=300, max_depth=6, random_state=42)
    rdg = Ridge(alpha=1.0)

    from sklearn.ensemble import VotingRegressor
    ensemble = VotingRegressor([("gbr", gbr), ("rf", rf), ("ridge", rdg)])
    ensemble.fit(X_train, y_train)

    preds = ensemble.predict(X_test)
    rmse  = math.sqrt(mean_squared_error(y_test, preds))
    r2    = r2_score(y_test, preds)
    print(f"[Model] RMSE={rmse:.4f}  R²={r2:.4f}", file=sys.stderr)

    # Feature importances from GBR sub-model
    gbr.fit(X_train, y_train)
    importances = dict(zip(feats, gbr.feature_importances_.tolist()))

    meta = {"features": feats, "rmse": round(rmse, 4), "r2": round(r2, 4),
            "importances": importances, "n_train": len(X_train)}

    joblib.dump({"model": ensemble, "meta": meta}, MODEL_PATH)
    return ensemble, meta

# Load or train
if os.path.exists(MODEL_PATH):
    try:
        _bundle = joblib.load(MODEL_PATH)
        _model  = _bundle["model"]
        _meta   = _bundle["meta"]
        # Re-train if old model doesn't have new features
        if len(_meta.get("features", [])) < 10:
            raise ValueError("stale model")
        print("[Boot] Loaded cached model.", file=sys.stderr)
    except Exception as e:
        print(f"[Boot] Re-training: {e}", file=sys.stderr)
        _model, _meta = train_model()
else:
    print("[Boot] Training model…", file=sys.stderr)
    _model, _meta = train_model()

# ─────────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model_meta": _meta})


@app.route("/api/search", methods=["GET"])
def search():
    import difflib, re

    raw = request.args.get("title", "").strip()
    if not raw:
        return jsonify({"error": "title required"}), 400

    # ── Normalise: collapse spaces, strip special chars gently ──
    def clean(t):
        t = re.sub(r"[^\w\s'-]", " ", t)
        return re.sub(r"\s+", " ", t).strip()

    title = clean(raw)

    # ── Try up to 3 OMDB query variants ──
    candidates = [title]
    # Drop trailing year-like token if present (e.g. "inception 2010")
    without_year = re.sub(r"\b(19|20)\d{2}\b", "", title).strip()
    if without_year and without_year != title:
        candidates.append(without_year)
    # Also try first 2 words if query is long
    words = title.split()
    if len(words) > 3:
        candidates.append(" ".join(words[:3]))

    omdb_results = []
    for q in candidates:
        try:
            r = requests.get(OMDB_BASE, params={"s": q, "apikey": OMDB_KEY}, timeout=10).json()
            hits = [m for m in r.get("Search", []) if m.get("Type") == "movie"]
            omdb_results.extend(hits)
            if hits:
                break                 # stop as soon as we get results
        except:
            pass

    # ── TMDB parallel search (for posters & overview) ──
    tmdb_results = []
    try:
        tr = requests.get(f"{TMDB_BASE}/search/movie",
                          params={"api_key": TMDB_KEY, "query": title}, timeout=10).json()
        tmdb_results = tr.get("results", [])
    except:
        pass

    # If OMDB empty but TMDB has results, synthesise basic entries
    if not omdb_results and tmdb_results:
        for t in tmdb_results[:8]:
            omdb_results.append({
                "imdbID":   "",
                "Title":    t.get("title", ""),
                "Year":     str(t.get("release_date", ""))[:4],
                "Type":     "movie",
                "Poster":   (TMDB_IMG + t["poster_path"]) if t.get("poster_path") else "N/A",
            })

    # ── Build TMDB lookup by title+year ──
    tmdb_map = {}
    for t in tmdb_results:
        key = (t.get("title", "").lower(), str(t.get("release_date", ""))[:4])
        tmdb_map[key] = t

    # ── Deduplicate OMDB hits by imdbID ──
    seen, deduped = set(), []
    for m in omdb_results:
        k = m.get("imdbID") or m.get("Title", "")
        if k not in seen:
            seen.add(k)
            deduped.append(m)

    # ── Rank by title similarity to original query ──
    def sim(title_str):
        return difflib.SequenceMatcher(None, raw.lower(), title_str.lower()).ratio()

    deduped.sort(key=lambda m: sim(m.get("Title", "")), reverse=True)

    results = []
    for m in deduped[:9]:
        key    = (m.get("Title", "").lower(), str(m.get("Year", ""))[:4])
        td     = tmdb_map.get(key, {})
        poster = m.get("Poster", "")
        if (not poster or poster == "N/A") and td.get("poster_path"):
            poster = TMDB_IMG + td["poster_path"]
        results.append({
            "imdb_id":     m.get("imdbID"),
            "title":       m.get("Title"),
            "year":        m.get("Year"),
            "poster":      poster,
            "tmdb_id":     td.get("id"),
            "tmdb_rating": td.get("vote_average"),
            "overview":    td.get("overview", ""),
        })

    return jsonify({"results": results, "query_used": title})



@app.route("/api/predict", methods=["GET"])
def predict():
    imdb_id = request.args.get("imdb_id", "").strip()
    title   = request.args.get("title", "").strip()
    if not imdb_id and not title:
        return jsonify({"error": "Provide imdb_id or title"}), 400

    # ── OMDB ──
    params = {"apikey": OMDB_KEY, "plot": "short"}
    if imdb_id: params["i"] = imdb_id
    else:       params["t"] = title
    omdb = requests.get(OMDB_BASE, params=params, timeout=10).json()
    if omdb.get("Response") == "False":
        return jsonify({"error": omdb.get("Error", "Movie not found")}), 404

    # ── TMDB (by IMDb ID) ──
    tmdb_stub    = tmdb_find_by_imdb(omdb.get("imdbID", ""))
    tmdb_id      = tmdb_stub.get("id")
    tmdb_full    = tmdb_details(tmdb_id) if tmdb_id else tmdb_search(omdb.get("Title", ""), omdb.get("Year"))

    # ── Ratings from all platforms ──
    imdb_actual  = safe_float(omdb.get("imdbRating", "N/A"), None) \
                   if omdb.get("imdbRating", "N/A") != "N/A" else None
    mc_raw       = omdb.get("Metascore", "N/A")
    mc_score     = safe_float(mc_raw, None) if mc_raw != "N/A" else None
    rt_raw       = None
    for r in omdb.get("Ratings", []):
        if "Rotten Tomatoes" in r.get("Source", ""):
            rt_raw = r.get("Value", None)
            break
    tmdb_score   = safe_float(tmdb_full.get("vote_average", "N/A"), None) \
                   if tmdb_full.get("vote_average") else None
    tmdb_votes   = safe_int(tmdb_full.get("vote_count", 0), 0)
    tmdb_pop     = safe_float(tmdb_full.get("popularity", 0), 0)
    budget       = safe_int(tmdb_full.get("budget", 0), 0)
    revenue      = safe_int(tmdb_full.get("revenue", 0), 0)
    tagline      = tmdb_full.get("tagline", "")
    tmdb_genres  = ", ".join(g["name"] for g in tmdb_full.get("genres", []))

    # Poster priority: OMDB → TMDB
    poster = omdb.get("Poster", "")
    if (not poster or poster == "N/A") and tmdb_full.get("poster_path"):
        poster = TMDB_IMG + tmdb_full["poster_path"]
    backdrop = ""
    if tmdb_full.get("backdrop_path"):
        backdrop = "https://image.tmdb.org/t/p/w1280" + tmdb_full["backdrop_path"]

    # ── Prediction ──
    X         = build_features(omdb, tmdb_full)
    predicted = float(_model.predict(X)[0])
    predicted = round(max(1.0, min(10.0, predicted)), 2)

    def sentiment(v):
        if v >= 9.0: return ("Masterpiece", "")
        if v >= 8.5: return ("Outstanding", "")
        if v >= 7.5: return ("Great", "")
        if v >= 6.5: return ("Good", "")
        if v >= 5.0: return ("Average", "")
        if v >= 3.0: return ("Poor", "")
        return ("Terrible", "")

    lbl, _emoji = sentiment(predicted)
    senti_label  = lbl

    return jsonify({
        # Core
        "title":         omdb.get("Title"),
        "year":          omdb.get("Year"),
        "genre":         tmdb_genres or omdb.get("Genre"),
        "director":      omdb.get("Director"),
        "actors":        omdb.get("Actors"),
        "plot":          omdb.get("Plot"),
        "tagline":       tagline,
        "poster":        poster,
        "backdrop":      backdrop,
        "runtime":       omdb.get("Runtime"),
        "language":      omdb.get("Language"),
        "country":       omdb.get("Country"),
        "awards":        omdb.get("Awards"),
        "rated":         omdb.get("Rated"),
        "imdb_id":       omdb.get("imdbID"),
        "tmdb_id":       tmdb_id,
        # Financial
        "budget":        budget,
        "revenue":       revenue,
        # Multi-platform ratings
        "ratings": {
            "imdb":        imdb_actual,
            "imdb_votes":  omdb.get("imdbVotes"),
            "metacritic":  mc_score,
            "rotten_tomatoes": rt_raw,
            "tmdb":        tmdb_score,
            "tmdb_votes":  tmdb_votes,
            "tmdb_popularity": round(tmdb_pop, 1),
        },
        # Prediction
        "predicted_rating": predicted,
        "sentiment":        senti_label,
        "model_r2":         _meta.get("r2"),
        "model_rmse":       _meta.get("rmse"),
        "feature_importances": _meta.get("importances", {}),
    })


@app.route("/api/retrain", methods=["POST"])
def retrain():
    global _model, _meta
    _model, _meta = train_model()
    return jsonify({"status": "retrained", "meta": _meta})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
