import os, joblib, torch, numpy as np, pandas as pd
from datetime import datetime
from .schemas import InputData
from .tabm_model import load_model, head_dims, TabMMultiHead
from sentence_transformers import SentenceTransformer


BASE_DIR = os.path.dirname(__file__)

scaler = joblib.load(os.path.join(BASE_DIR, "pkl_files", "scaler.pkl"))
label_encoders = joblib.load(os.path.join(BASE_DIR, "pkl_files", "label_encoders.pkl"))
tables = joblib.load(os.path.join(BASE_DIR, "pkl_files", "group_stats.pkl"))  
sentence_model = SentenceTransformer(os.path.join(BASE_DIR, "pkl_files", "sentence_model"))

CATEGORICAL_FEATURES = ['country_displayable_name', "dur_bin",]
CYCLIC_NUMERIC = [
    'deadline_mon_sin','deadline_mon_cos','deadline_dom_sin','deadline_dom_cos',
    'launched_at_mon_sin','launched_at_mon_cos','launched_at_dom_sin','launched_at_dom_cos'
]
NUMERIC_FEATURES = ["launch_dow","deadline_dow","prep_days",
        "days_diff_launched_at_deadline","days_diff_launched_at_deadline_log",
        "too_short_or_long","name_len","blurb_len","has_video","has_photo",
        "goal_usd_log","goal_per_day_log",
        "gpd_rank_in_cat_mon","goal_rank_in_cat_mon",
        "gpd_vs_cat_country_med","goal_vs_cat_country_med",
        "cat_30d_launch_density","cat_30d_density_z",
        "cat_mon_n","cat_mon_goal_med","cat_mon_gpd_med",]

cat_cardinalities = [len(label_encoders[f].classes_) for f in CATEGORICAL_FEATURES]

device = torch.device("cpu")

model = load_model(os.path.join(BASE_DIR, "tabm_model.pth"), device=device)

def cyclic_encode(dt: datetime, prefix: str):
    return {
        f"{prefix}_mon_sin": np.sin(2*np.pi*(dt.month-1)/12),
        f"{prefix}_mon_cos": np.cos(2*np.pi*(dt.month-1)/12),
        f"{prefix}_dom_sin": np.sin(2*np.pi*(dt.day-1)/31),
        f"{prefix}_dom_cos": np.cos(2*np.pi*(dt.day-1)/31),
    }

def preprocess(data: InputData):
    print("📦 preprocess received data:", data)

    start = datetime.fromisoformat(data.start_date)
    end = datetime.fromisoformat(data.end_date)
    duration = (end - start).days

    # ---- duration bin ----
    if duration <= 29:
        dur_bin = "<30"
    elif duration <= 45:
        dur_bin = "30-45"
    elif duration <= 60:
        dur_bin = "46-60"
    else:
        dur_bin = ">60"

    too_short_or_long = int(duration < 30 or duration > 60)

    # ---- numeric features ----
    feats_num = {
        "launch_dow": start.weekday(),
        "deadline_dow": end.weekday(),
        "prep_days": 0,
        "days_diff_launched_at_deadline": duration,
        "days_diff_launched_at_deadline_log": np.log1p(duration),
        "too_short_or_long": too_short_or_long,
        "name_len": len((data.name or "")),
        "blurb_len": len((data.blurb or "")),
        "has_video": data.has_video,
        "has_photo": data.has_photo,
        "goal_usd_log": np.log1p(data.goal),
        "goal_per_day_log": np.log1p(data.goal / max(duration, 1)),
    }

    # ---- group stats lookup ----
    key = (data.country_displayable_name, dur_bin)
    g_stat = tables.get(key)
    if g_stat is None:
        print(f"[WARN] Missing group_stats key: {key} → using defaults")
        g_stat = {
            "gpd_rank_in_cat_mon": 0,
            "goal_rank_in_cat_mon": 0,
            "gpd_vs_cat_country_med": 1.0,
            "goal_vs_cat_country_med": 1.0,
            "cat_30d_launch_density": 0,
            "cat_30d_density_z": 0,
            "cat_mon_n": 0,
            "cat_mon_goal_med": 0,
            "cat_mon_gpd_med": 0,
        }
    feats_num.update(g_stat)

    # ---- numeric scaling ----
    X_num = np.array([[feats_num[f] for f in feats_num]])
    X_num_scaled = scaler.transform(X_num)

    # ---- text embedding ----
    combined = f"{(data.name or '')}. {(data.blurb or '')}"
    X_embed = sentence_model.encode([combined], normalize_embeddings=True).astype(np.float32)

    # ---- cyclic encoding ----
    cyclic = {}
    cyclic.update(cyclic_encode(start, "launched_at"))
    cyclic.update(cyclic_encode(end, "deadline"))
    X_cyclic = np.array([[cyclic[f] for f in CYCLIC_NUMERIC]])

    # ---- final numeric ----
    x_num = np.concatenate([X_num_scaled, X_embed, X_cyclic], axis=1).astype(np.float32)

    # ---- categorical ----
    x_cat = []
    for f in CATEGORICAL_FEATURES:
        le = label_encoders[f]
        if f == "dur_bin":
            raw_val = dur_bin
        else:
            raw_val = getattr(data, f)

        raw_val = str(raw_val) if raw_val is not None else "missing"

        if raw_val in le.classes_:
            val = le.transform([raw_val])[0]
        else:
            print(f"[WARN] Unknown category for {f}: {raw_val} → fallback to 0")
            val = 0
        x_cat.append(val)

    # ---- convert to tensor ----
    x_num = torch.tensor(x_num, dtype=torch.float32)
    x_cat = torch.tensor([x_cat], dtype=torch.long)
    
    print(label_encoders["country_displayable_name"].classes_[:50])  
    print("=== BACKEND DEBUG ===")
    print("Numeric feats (scaled):", X_num_scaled[0][:5])
    print("Text embed (sbert):", X_embed[0][:5])
    print("Cyclic feats:", X_cyclic[0].tolist())
    print("x_num shape:", x_num.shape)
    print("x_cat:", x_cat.tolist())
    
    return x_num, x_cat




