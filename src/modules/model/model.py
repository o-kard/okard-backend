import os, joblib, torch, numpy as np, pandas as pd
from datetime import datetime
from .schemas import InputData
from .tabm_model import load_model, head_dims, TabMMultiHead

BASE_DIR = os.path.dirname(__file__)

scaler = joblib.load(os.path.join(BASE_DIR, "scaler.pkl"))
tfidf = joblib.load(os.path.join(BASE_DIR, "tfidf.pkl"))
svd = joblib.load(os.path.join(BASE_DIR, "svd.pkl"))
label_encoders = joblib.load(os.path.join(BASE_DIR, "label_encoders.pkl"))
tables = joblib.load(os.path.join(BASE_DIR, "group_stats.pkl"))  

CATEGORICAL_FEATURES = ["currency", "country_displayable_name", "location_state", "dur_bin",]
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

# print("NUMERIC_FEATURES:", len(NUMERIC_FEATURES))
# print("svd:", svd.n_components)
# print("cyclic:", len(CYCLIC_NUMERIC))
# print("total:", len(NUMERIC_FEATURES) + svd.n_components + len(CYCLIC_NUMERIC))

device = torch.device("cpu")
model = load_model(
    n_num_features=len(NUMERIC_FEATURES) + svd.n_components + len(CYCLIC_NUMERIC),
    cat_cardinalities=cat_cardinalities,
    head_dims=head_dims,
    model_path=os.path.join(BASE_DIR, "model.pth"),
    device=device,
)

def cyclic_encode(dt: datetime, prefix: str):
    return {
        f"{prefix}_mon_sin": np.sin(2*np.pi*(dt.month-1)/12),
        f"{prefix}_mon_cos": np.cos(2*np.pi*(dt.month-1)/12),
        f"{prefix}_dom_sin": np.sin(2*np.pi*(dt.day-1)/31),
        f"{prefix}_dom_cos": np.cos(2*np.pi*(dt.day-1)/31),
    }

def preprocess(data: InputData):
    start = datetime.fromisoformat(data.start_date)
    end = datetime.fromisoformat(data.end_date)
    duration = (end - start).days

    # --- คำนวณ dur_bin ---
    if duration <= 29:
        dur_bin = "<30"
    elif duration <= 45:
        dur_bin = "30-45"
    elif duration <= 60:
        dur_bin = "46-60"
    else:
        dur_bin = ">60"

    too_short_or_long = int(duration < 30 or duration > 60)

    feats_num = {
        "launch_dow": start.weekday(),
        "deadline_dow": end.weekday(),
        "prep_days": 0,
        "days_diff_launched_at_deadline": duration,
        "days_diff_launched_at_deadline_log": np.log1p(duration),
        "too_short_or_long": too_short_or_long,
        "name_len": len(data.name or ""),
        "blurb_len": len(data.blurb or ""),
        "has_video": data.has_video,
        "has_photo": data.has_photo,
        "goal_usd_log": np.log1p(data.goal),
        "goal_per_day_log": np.log1p(data.goal / max(duration, 1)),
    }

    # lookup group stats
    key = (data.currency, data.country_displayable_name, data.location_state, dur_bin)
    g_stat = tables.get(key, {
        "gpd_rank_in_cat_mon": 0,
        "goal_rank_in_cat_mon": 0,
        "gpd_vs_cat_country_med": 1.0,
        "goal_vs_cat_country_med": 1.0,
        "cat_30d_launch_density": 0,
        "cat_30d_density_z": 0,
        "cat_mon_n": 0,
        "cat_mon_goal_med": 0,
        "cat_mon_gpd_med": 0,
    })
    feats_num.update(g_stat)

    # numeric + scale
    X_num = np.array([[feats_num[f] for f in feats_num]])
    X_num_scaled = scaler.transform(X_num)

    # text
    combined = (data.name or "") + " " + (data.blurb or "")
    X_svd = svd.transform(tfidf.transform([combined]))

    # cyclic
    cyclic = {}
    cyclic.update(cyclic_encode(start, "launched_at"))
    cyclic.update(cyclic_encode(end, "deadline"))
    X_cyclic = np.array([[cyclic[f] for f in CYCLIC_NUMERIC]])

    x_num = np.concatenate([X_num_scaled, X_svd, X_cyclic], axis=1).astype(np.float32)

    # categorical
    x_cat = []
    for f in CATEGORICAL_FEATURES:
        le = label_encoders[f]
        if f == "dur_bin":
            raw_val = dur_bin
        else:
            raw_val = getattr(data, f)

        val = le.transform([raw_val])[0] if raw_val in le.classes_ else 0
        x_cat.append(val)

    x_num = torch.tensor(x_num, dtype=torch.float32)
    x_cat = torch.tensor([x_cat], dtype=torch.long)

    return x_num, x_cat



